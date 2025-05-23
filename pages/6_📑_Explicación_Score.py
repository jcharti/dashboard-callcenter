
import streamlit as st

st.set_page_config(page_title="Explicación del Score", layout="wide")

st.title("📑 Explicación de KPIs y Score de Agentes")

st.header("📑 Cálculo del Apego al Guión")
st.markdown("""
El **Apego al Guión** se calcula como el promedio de cumplimiento por bloques del script definidos para cada campaña:

| Bloque       | Ejemplo de contenido            | Peso |
|--------------|----------------------------------|------|
| Saludo       | “Hola,habla…”                   | 20%  |
| Presentación | “Mi nombre es…”                 | 20%  |
| Oferta       | “La promoción incluye…”         | 20%  |
| Beneficios   | “Usted obtiene…”                | 20%  |
| Cierre       | “¿Confirmamos la compra?”       | 20%  |

Cada bloque se compara con la transcripción para determinar si fue mencionado correctamente.
""")

st.header("🧮 Cálculo del Score Total del Agente")
st.markdown("""
El **Score Total** se calcula como un promedio ponderado de los siguientes KPIs:

| KPI                   | Descripción                                                 | Peso |
|------------------------|-------------------------------------------------------------|------|
| 🟢 Apego al Guión       | Coincidencia con el script en bloques clave                 | 60%  |
| 🔵 Velocidad de habla   | Palabras por minuto (entre 90 y 140 wpm es ideal)           | 20%  |
| 🔴 Fricción detectada   | % de frases negativas u objeciones del cliente detectadas   | 20%  |
""")
