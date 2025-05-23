
import streamlit as st

st.set_page_config(page_title="Inicio", layout="wide")
st.title("🎯 Sistema de Calidad para Call Centers")

st.markdown("## 🧭 Objetivo del Sistema")
st.markdown(
    """
    Este sistema permite **medir y mejorar la calidad del servicio** telefónico en un call center,
    a través del análisis automatizado de las llamadas realizadas por los agentes.

    Utiliza inteligencia artificial para transcribir los audios y calcular indicadores como:

    - 📜 **Apego al guión**: ¿qué tan bien sigue el agente el guión propuesto?
    - 🗣️ **Velocidad de habla (WPM)**: ¿habla demasiado rápido o demasiado lento?
    - ⚠️ **Fricción en la llamada**: ¿hay muchas objeciones o negativas por parte del cliente?

    Toda la información se organiza por agente, campaña y fecha, y permite hacer análisis individuales y grupales.
    """
)

st.markdown("---")
st.markdown("## 🔄 Cómo funciona - Paso a Paso")

st.markdown("### 📂 Repositorio de Audios")
st.markdown("🎙️ Los archivos de audio deben estar disponibles en una carpeta compartida de Google Drive conectada al sistema.")

st.markdown("### 1️⃣ **Carga de Metadatos**")
st.markdown("📥 El sistema reconoce los audios cargados y te permite clasificar, agente, campaña y fechas.")

st.markdown("### 2️⃣ **Configuración de Campañas y Scripts**")
st.markdown("📝 Crea campañas y sube sus Scripts en formato Word o PDF.")

st.markdown("### 3️⃣ **Procesamiento de Audios**")
st.markdown("🧠 El sistema transcribe los audios y detecta los bloques del guión.")

st.markdown("### 4️⃣ **Visualización de Indicadores**")
st.markdown("📊 Explora dashboards por agente y campaña. Detecta mejoras y brechas.")

st.markdown("### 5️⃣ **Revisión Detallada de Llamadas**")
st.markdown("🎧 Escucha llamadas, ve sus transcripciones y clasifícalas para retroalimentar.")

st.markdown("---")
st.info("Usa el menú lateral para navegar entre las funcionalidades disponibles.")
