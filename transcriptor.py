
import os
import whisper
import csv
import ffmpeg
import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
from tqdm import tqdm

# Configuración
audio_dir = "audios"
transcripcion_dir = "transcripciones"
metadatos_path = "metadatos.csv"
resumen_path = "resumen.csv"
script_path = "script_campana_bloques.csv"
no_procesados_path = "no_procesados.csv"

os.makedirs(transcripcion_dir, exist_ok=True)

# Frases clave
SALUDOS = ["hola", "buenos días", "buenas tardes", "le habla"]
CONSENTIMIENTO = ["consentimiento", "autorización", "permite grabar"]
CIERRES = ["envío contrato", "queda registrado", "confirmo su compra", "formalizar"]
PRECIOS = ["precio", "costo", "valor", "cuota", "montos"]
OBJECIONES = ["no me interesa", "lo voy a pensar", "muy caro", "no puedo ahora", "ya lo vi", "no estoy interesado"]

# Cargar modelo Whisper
print("🔁 Cargando modelo Whisper (base)...")
model = whisper.load_model("base")

# Cargar scripts por bloques
bloques = ["Saludo", "Presentación", "Oferta", "Beneficios", "Cierre"]
df_script = pd.read_csv(script_path) if os.path.exists(script_path) else pd.DataFrame(columns=["Campaña"] + bloques)

def obtener_script_bloques(campaña):
    fila = df_script[df_script["Campaña"] == campaña]
    return fila.iloc[0].to_dict() if not fila.empty else {}

def calcular_apego_bloques(script_dict, transcripcion):
    if not script_dict:
        return 0.0, {}
    total_score, detalle = 0.0, {}
    for bloque in bloques:
        contenido = script_dict.get(bloque, "")
        palabras_script = set(contenido.lower().split())
        palabras_trans = set(transcripcion.lower().split())
        comunes = palabras_script.intersection(palabras_trans)
        score = len(comunes) / len(palabras_script) * 100 if palabras_script else 0
        detalle[bloque] = round(score, 1)
        total_score += score
    return round(total_score / len(bloques), 1), detalle

def contiene_frases(texto, frases):
    return any(f in texto.lower() for f in frases)

def detectar_consentimiento_afirmativo(texto):
    lower_text = texto.lower()
    return {
        "consentimiento": contiene_frases(lower_text, CONSENTIMIENTO),
        "respuesta_positiva": any(p in lower_text for p in ["sí", "claro", "por supuesto", "correcto"])
    }

def obtener_duracion_audio(path_audio):
    try:
        probe = ffmpeg.probe(path_audio)
        return float(probe["format"]["duration"])
    except:
        return 0.0

def validar_fecha(fecha_str):
    try:
        datetime.strptime(str(fecha_str), "%Y-%m-%d")
        return True
    except:
        return False

def evaluar_velocidad(wpm):
    if wpm < 90:
        return "Lenta", 0.5
    elif wpm > 140:
        return "Rápida", 0.5
    else:
        return "Adecuada", 1.0

def evaluar_friccion(porcentaje):
    if porcentaje <= 5:
        return "Baja", 1.0
    elif porcentaje <= 15:
        return "Media", 0.75
    else:
        return "Alta", 0.5

def calcular_score_total(apego, wpm, friccion_pct):
    _, puntaje_wpm = evaluar_velocidad(wpm)
    _, puntaje_friccion = evaluar_friccion(friccion_pct)
    return round(apego * 0.6 + puntaje_wpm * 100 * 0.2 + puntaje_friccion * 100 * 0.2, 1)

# Procesar audios
metadatos = pd.read_csv(metadatos_path)
resumen = []
no_procesados = []

audios_lista = [a for a in os.listdir(audio_dir) if a.endswith((".mp3", ".wav", ".m4a"))]

for archivo in tqdm(audios_lista, desc="Procesando audios"):
    if archivo not in metadatos["Archivo"].values:
        no_procesados.append([archivo, "No está en metadatos"])
        continue

    fila = metadatos[metadatos["Archivo"] == archivo].iloc[0]
    agente, campaña, fecha = fila["Agente"], fila["Campaña"], fila["Fecha"]

    if not all([agente, campaña, fecha]) or not validar_fecha(fecha):
        no_procesados.append([archivo, "Datos incompletos o fecha inválida"])
        continue

    path_audio = os.path.join(audio_dir, archivo)
    transcripcion = model.transcribe(path_audio, language="Spanish")["text"].strip()

    palabras = len(transcripcion.split())
    duracion_min = round(obtener_duracion_audio(path_audio) / 60, 2)
    ppm = round(palabras / duracion_min, 2) if duracion_min > 0 else 0
    preview = " ".join(transcripcion.split()[:20]) + "..."

    saludo = contiene_frases(transcripcion, SALUDOS)
    objecion = contiene_frases(transcripcion, OBJECIONES)
    cierre = contiene_frases(transcripcion, CIERRES)
    precio = contiene_frases(transcripcion, PRECIOS)
    consentimiento = detectar_consentimiento_afirmativo(transcripcion)

    script_dict = obtener_script_bloques(campaña)
    apego_total, detalle = calcular_apego_bloques(script_dict, transcripcion)

    friccion_pct = 0
    for frase in OBJECIONES:
        if frase in transcripcion.lower():
            friccion_pct += 1
    total_frases = len(transcripcion.split(".")) or 1
    friccion_pct = round((friccion_pct / total_frases) * 100, 2)

    eval_wpm, _ = evaluar_velocidad(ppm)
    eval_fric, _ = evaluar_friccion(friccion_pct)
    score_total = calcular_score_total(apego_total, ppm, friccion_pct)

    resultado = "Exitoso" if cierre and not objecion else "No Exitoso" if objecion and not cierre else "Indeterminado"

    fila_resumen = [
        archivo, agente, campaña, fecha, palabras, duracion_min, ppm,
        saludo, consentimiento["consentimiento"], consentimiento["respuesta_positiva"],
        precio, cierre, objecion, resultado, preview,
        apego_total, ppm, eval_wpm, friccion_pct, eval_fric, score_total
    ]
    for b in bloques:
        fila_resumen.append(detalle.get(b, 0.0))
    resumen.append(fila_resumen)

with open(resumen_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Archivo", "Agente", "Campaña", "Fecha", "Palabras", "Duración (min)", "Palabras/min",
        "Saludo Detectado", "Consentimiento Solicitado", "Consentimiento Afirmado",
        "Precio Mencionado", "Cierre Detectado", "Objeción Detectada", "Resultado Estimado", "Preview",
        "Apego al Guion (%)", "WPM", "Evaluación WPM", "Friccion (%)", "Evaluación Fricción", "Score Total"
    ] + [f"% {b}" for b in bloques])
    writer.writerows(resumen)

if no_procesados:
    with open(no_procesados_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Archivo", "Motivo"])
        writer.writerows(no_procesados)

print("✅ Proceso completado.")
