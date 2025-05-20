
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime

st.title("🛠️ Dashboard Operativo - Supervisión y Calidad")

# Cargar datos
try:
    df = pd.read_csv("resumen.csv", parse_dates=["Fecha"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
except Exception as e:
    st.error(f"Error al cargar 'resumen.csv': {e}")
    st.stop()

# Sidebar de filtros
st.sidebar.header("🎛️ Filtros")
campañas = df["Campaña"].dropna().unique().tolist()
agentes = df["Agente"].dropna().unique().tolist()
fecha_min = df["Fecha"].min()
fecha_max = df["Fecha"].max()

campaña_sel = st.sidebar.multiselect("Campaña", campañas, default=campañas)
agente_sel = st.sidebar.multiselect("Agente", agentes, default=agentes)
fecha_rango = st.sidebar.date_input("Rango de Fechas", (fecha_min.date(), fecha_max.date()))

# Filtrar dataset
df_filtrado = df[
    (df["Campaña"].isin(campaña_sel)) &
    (df["Agente"].isin(agente_sel)) &
    (df["Fecha"] >= pd.to_datetime(fecha_rango[0])) &
    (df["Fecha"] <= pd.to_datetime(fecha_rango[1]))
]

# Indicadores de cumplimiento
st.subheader("✅ Cumplimiento de Protocolo por Agente")
cumplimiento = df_filtrado.groupby("Agente").agg({
    "Saludo Detectado": "mean",
    "Consentimiento Solicitado": "mean",
    "Consentimiento Afirmado": "mean",
    "Cierre Detectado": "mean"
}).reset_index()
cumplimiento.columns = ["Agente", "% Saludo", "% Solicita Consentimiento", "% Consentimiento Afirmado", "% Cierre Detectado"]
cumplimiento[[col for col in cumplimiento.columns if col != "Agente"]] = cumplimiento[[col for col in cumplimiento.columns if col != "Agente"]] * 100
cols_numericas = [col for col in cumplimiento.columns if col != "Agente"]
st.dataframe(cumplimiento.style.format({col: "{:.1f}" for col in cols_numericas}), use_container_width=True)

# Objeciones por agente
st.subheader("❗ Distribución de Objeciones por Agente")
fig_obj = px.bar(
    df_filtrado.groupby("Agente")["Objeción Detectada"].mean().reset_index(name="% con Objeción").assign(**{"% con Objeción": lambda d: d["% con Objeción"] * 100}),
    x="Agente",
    y="% con Objeción",
    title="Porcentaje de llamadas con objeción",
    text_auto=True
)
st.plotly_chart(fig_obj, use_container_width=True)

# Transcripciones
st.subheader("📝 Revisión Rápida de Transcripciones")
st.dataframe(
    df_filtrado[[
        "Fecha", "Archivo", "Agente", "Campaña",
        "Consentimiento Afirmado", "Objeción Detectada",
        "Resultado Estimado", "Preview"
    ]].sort_values(by="Fecha", ascending=False),
    use_container_width=True
)

# Exportar CSV
st.subheader("⬇️ Exportar Datos para Auditoría")
csv_buffer = StringIO()
df_filtrado.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 Descargar CSV",
    data=csv_buffer.getvalue(),
    file_name="auditoria_llamadas.csv",
    mime="text/csv"
)

st.caption("🔍 Panel diseñado para supervisores de calidad y auditores de procesos de atención.")
