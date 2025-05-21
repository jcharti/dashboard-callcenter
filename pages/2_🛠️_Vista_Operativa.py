
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vista Operativa", layout="wide")
st.title("🛠️ Vista Operativa")

# Cargar resumen
try:
    df = pd.read_csv("resumen.csv", parse_dates=["Fecha"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
except Exception as e:
    st.error(f"Error al cargar resumen.csv: {e}")
    st.stop()

# Filtros
col1, col2 = st.columns(2)
campañas = df["Campaña"].dropna().unique().tolist()
agentes = df["Agente"].dropna().unique().tolist()

with col1:
    campana_sel = st.selectbox("Filtrar por campaña:", ["Todas"] + campañas)
with col2:
    agente_sel = st.selectbox("Filtrar por agente:", ["Todos"] + agentes)

# Aplicar filtros
df_filtrado = df.copy()
if campana_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Campaña"] == campana_sel]
if agente_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Agente"] == agente_sel]

st.markdown("### 🎧 Detalle de llamadas transcritas")
st.dataframe(df_filtrado[[
    "Archivo", "Agente", "Campaña", "Fecha",
    "Saludo Detectado", "Consentimiento Solicitado", "Consentimiento Afirmado",
    "Precio Mencionado", "Cierre Detectado", "Objeción Detectada",
    "Resultado Estimado", "Score Total", "Apego al Guion (%)",
    "% Saludo", "% Presentación", "% Oferta", "% Beneficios", "% Cierre"
]], use_container_width=True)

st.markdown("#### 🔎 Vista previa del inicio de la llamada")
for i, row in df_filtrado.iterrows():
    st.caption(f"{row['Archivo']} - {row['Fecha']} - {row['Agente']}")
    st.text(row["Preview"])
