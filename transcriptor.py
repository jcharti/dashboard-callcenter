import os
import whisper
import csv
import ffmpeg
import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
from tqdm import tqdm  # <--- NUEVO

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

# Cargar modelo Whisper con mejor calidad
print("🔁 Cargando modelo Whisper (medium)...")
model = whisper.load_model("medium")

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
    return any(frase in texto.lower() for frase in frases)

def detectar_consentimiento_afirmativo(texto):
    palabras = texto.lower().split()
    resultado = {"consentimiento": False, "respuesta_positiva": False}
    for i, palabra in enumerate(palabras):
        if "consentimiento" in palabra:
            resultado["consentimiento"] = True
            siguientes = palabras[i+1:i+6]
            if any(w in ["sí", "claro", "correcto"] for w in siguientes):
                resultado["respuesta_positiva"] = True
                break
    return resultado

def obtener_duracion_audio(path):
    try:
        probe = ffmpeg.probe(path)
        return float(probe["format"]["duration"])
    except:
        return 0.0

def validar_fecha(fecha_str):
    try:
        datetime.strptime(str(fecha_str), "%Y-%m-%d")
        return True
    except:
        return False

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

    score = apego_total * 0.5 + (15 if saludo else 0) + (20 if cierre else 0) + (15 if consentimiento["respuesta_positiva"] else 0)

    if cierre and not objecion:
        resultado = "Exitoso"
    elif objecion and not cierre:
        resultado = "No Exitoso"
    else:
        resultado = "Indeterminado"

    resumen.append([
        archivo, agente, campaña, fecha, palabras, duracion_min, ppm,
        saludo, consentimiento["consentimiento"], consentimiento["respuesta_positiva"],
        precio, cierre, objecion, resultado, preview,
        apego_total, round(score, 1)
    ] + [detalle.get(b, 0.0) for b in bloques])

# Guardar resumen
with open(resumen_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Archivo", "Agente", "Campaña", "Fecha", "Palabras", "Duración (min)", "Palabras/min",
        "Saludo Detectado", "Consentimiento Solicitado", "Consentimiento Afirmado",
        "Precio Mencionado", "Cierre Detectado", "Objeción Detectada", "Resultado Estimado", "Preview",
        "Apego al Guion (%)", "Score Total"
    ] + [f"% {b}" for b in bloques])
    writer.writerows(resumen)

if no_procesados:
    with open(no_procesados_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Archivo", "Motivo"])
        writer.writerows(no_procesados)

print("✅ Proceso completado.")
