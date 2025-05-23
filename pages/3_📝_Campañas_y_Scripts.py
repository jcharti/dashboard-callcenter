
import streamlit as st
import pandas as pd
import os
import docx
import pdfplumber

st.set_page_config(page_title="Campañas y Scripts", layout="wide")
st.title("🧩 Administración de Campañas y Scripts por Bloques")

SCRIPTS_PATH = "script_campana_bloques.csv"
BLOQUES = ["Saludo", "Presentación", "Oferta", "Beneficios", "Cierre"]

# Cargar base actual si existe
if os.path.exists(SCRIPTS_PATH):
    df_scripts = pd.read_csv(SCRIPTS_PATH)
else:
    df_scripts = pd.DataFrame(columns=["Campaña"] + BLOQUES)

st.subheader("📋 Campañas registradas")
if not df_scripts.empty:
    st.dataframe(df_scripts)
else:
    st.info("No hay campañas registradas.")

st.subheader("➕ Crear nueva campaña y cargar script")

nombre_campaña = st.text_input("Nombre de la nueva campaña")
archivo = st.file_uploader("Sube el archivo del script (.docx o .pdf)", type=["docx", "pdf"])

def extraer_texto_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extraer_texto_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def buscar_bloques(texto):
    texto = texto.lower()
    bloques_extraidos = {bloque: "" for bloque in BLOQUES}
    lines = texto.splitlines()

    for i, line in enumerate(lines):
        l = line.lower()
        if "hola" in l or "buenos días" in l or "le habla" in l:
            bloques_extraidos["Saludo"] += line + " "
        elif "mi nombre" in l or "estoy llamando" in l:
            bloques_extraidos["Presentación"] += line + " "
        elif "ofrezco" in l or "incluye" in l or "promoción" in l:
            bloques_extraidos["Oferta"] += line + " "
        elif "beneficio" in l or "usted obtiene" in l:
            bloques_extraidos["Beneficios"] += line + " "
        elif "confirmamos" in l or "interesa" in l or "formalizar" in l:
            bloques_extraidos["Cierre"] += line + " "

    return bloques_extraidos

if archivo and nombre_campaña:
    if archivo.name.endswith(".docx"):
        texto_extraido = extraer_texto_docx(archivo)
    else:
        texto_extraido = extraer_texto_pdf(archivo)

    st.success("✅ Texto extraído correctamente. Revisa y edita los bloques:")
    st.text_area("Texto completo extraído", texto_extraido, height=200)

    bloques_detectados = buscar_bloques(texto_extraido)
    st.markdown("### ✏️ Edita el contenido de cada bloque")

    datos = {"Campaña": nombre_campaña}
    for bloque in BLOQUES:
        datos[bloque] = st.text_area(f"{bloque}", bloques_detectados.get(bloque, ""), height=100)

    if st.button("💾 Guardar campaña y script"):
        df_scripts = pd.concat([df_scripts, pd.DataFrame([datos])], ignore_index=True)
        df_scripts.to_csv(SCRIPTS_PATH, index=False)
        st.success("🚀 Campaña guardada exitosamente. Puedes comenzar a usarla.")
else:
    st.info("Ingresa el nombre de la campaña y sube un archivo .docx o .pdf.")
