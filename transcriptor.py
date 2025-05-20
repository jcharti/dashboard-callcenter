import os
import whisper
import csv
import ffmpeg
import pandas as pd
from datetime import datetime

# Configuración
audio_dir = "audios"
transcripcion_dir = "transcripciones"
metadatos_path = "metadatos.csv"
resumen_path = "resumen.csv"
no_procesados_path = "no_procesados.csv"

os.makedirs(transcripcion_dir, exist_ok=True)

# Asegura acceso a ffmpeg
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

print("🔁 Cargando modelo Whisper (base)...")
model = whisper.load_model("base")

# Frases clave por grupo de KPI
SALUDOS = ["hola", "buenos días", "buenas tardes", "le habla"]
CONSENTIMIENTO = ["consentimiento", "autorización", "permite grabar"]
CIERRES = ["envío contrato", "queda registrado", "confirmo su compra", "formalizar"]
PRECIOS = ["precio", "costo", "valor", "cuota", "montos"]
OBJECIONES = ["no me interesa", "lo voy a pensar", "muy caro", "no puedo ahora", "ya lo vi", "no estoy interesado"]

# Funciones
def obtener_duracion_audio(path):
    try:
        probe = ffmpeg.probe(path)
        return float(probe["format"]["duration"])
    except Exception as e:
        print(f"⚠️ Error obteniendo duración: {e}")
        return 0.0

def contiene_frases(texto, frases):
    return any(frase.lower() in texto.lower() for frase in frases)

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

def validar_fecha(fecha_str):
    try:
        datetime.strptime(str(fecha_str), "%Y-%m-%d")
        return True
    except:
        return False

# Cargar metadatos
if not os.path.exists(metadatos_path):
    print("❌ No se encontró el archivo metadatos.csv")
    exit()

metadatos_df = pd.read_csv(metadatos_path, encoding="utf-8-sig")
metadatos_df.columns = [col.strip().replace("\ufeff", "") for col in metadatos_df.columns]

# Inicialización
filas_resumen = []
no_procesados = []

# Procesar audios
for archivo in os.listdir(audio_dir):
    if not archivo.endswith((".mp3", ".wav", ".m4a")):
        continue

    if archivo not in metadatos_df["Archivo"].values:
        print(f"⚠️ {archivo} omitido: no está en metadatos.csv")
        no_procesados.append([archivo, "No está en metadatos.csv"])
        continue

    fila = metadatos_df[metadatos_df["Archivo"] == archivo].iloc[0]
    agente = str(fila.get("Agente", "")).strip()
    campaña = str(fila.get("Campaña", "")).strip()
    fecha_str = str(fila.get("Fecha", "")).strip()

    if not agente or not campaña or not fecha_str:
        no_procesados.append([archivo, "Metadatos incompletos"])
        continue

    if not validar_fecha(fecha_str):
        no_procesados.append([archivo, "Fecha inválida"])
        continue

    ruta_audio = os.path.join(audio_dir, archivo)
    nombre_base = os.path.splitext(archivo)[0]
    ruta_txt = os.path.join(transcripcion_dir, f"{nombre_base}.txt")

    print(f"✅ Procesando: {archivo}")
    resultado = model.transcribe(ruta_audio, language="Spanish")
    texto = resultado["text"].strip()
    palabras = len(texto.split())
    duracion_seg = obtener_duracion_audio(ruta_audio)
    duracion_min = round(duracion_seg / 60, 2)
    palabras_por_min = round(palabras / duracion_min, 2) if duracion_min > 0 else 0

    saludo = contiene_frases(texto, SALUDOS)
    objecion = contiene_frases(texto, OBJECIONES)
    cierre = contiene_frases(texto, CIERRES)
    menciona_precio = contiene_frases(texto, PRECIOS)
    consentimiento_data = detectar_consentimiento_afirmativo(texto)
    preview = " ".join(texto.split()[:20]) + "..."

    if cierre and not objecion:
        resultado_estimado = "Exitoso"
    elif objecion and not cierre:
        resultado_estimado = "No Exitoso"
    else:
        resultado_estimado = "Indeterminado"

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)

    filas_resumen.append([
        archivo, agente, campaña, fecha_str,
        palabras, duracion_min, palabras_por_min,
        saludo, consentimiento_data["consentimiento"],
        consentimiento_data["respuesta_positiva"],
        menciona_precio, cierre, objecion,
        resultado_estimado, preview
    ])

# Guardar resumen
with open(resumen_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Archivo", "Agente", "Campaña", "Fecha",
        "Palabras", "Duración (min)", "Palabras/min",
        "Saludo Detectado", "Consentimiento Solicitado",
        "Consentimiento Afirmado", "Precio Mencionado",
        "Cierre Detectado", "Objeción Detectada",
        "Resultado Estimado", "Preview"
    ])
    writer.writerows(filas_resumen)

# Guardar archivos no procesados
if no_procesados:
    with open(no_procesados_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Archivo no procesado", "Motivo"])
        writer.writerows(no_procesados)

print("\n✅ Proceso completado.")
print(f"→ {resumen_path}")
if no_procesados:
    print(f"→ {no_procesados_path} (audios omitidos)")
