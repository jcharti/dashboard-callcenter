
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")
st.title("📈 Dashboard Ejecutivo")

csv_path = "resumen.csv"
if not os.path.exists(csv_path):
    st.error("❌ No se encontró el archivo resumen.csv.")
    st.stop()

df = pd.read_csv(csv_path)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df = df.dropna(subset=["Fecha", "Campaña", "Agente", "Score Total"])

# KPIs globales simplificados
st.subheader("📌 KPIs globales")
col1, col2, col3 = st.columns(3)
col1.metric("Score Promedio", f"{df['Score Total'].mean():.1f}")
col2.metric("Score más bajo", f"{df['Score Total'].min():.1f}")
col3.metric("Score más alto", f"{df['Score Total'].max():.1f}")

# Score promedio por campaña
st.subheader("🏷️ Score promedio por campaña")
df_campañas = df.groupby("Campaña")["Score Total"].mean().round(1).reset_index()
fig_campañas = px.bar(df_campañas, x="Campaña", y="Score Total", color="Score Total", title="Ranking de campañas por score")
st.plotly_chart(fig_campañas, use_container_width=True)

# Evolución global del score
st.subheader("📊 Evolución global del Score Total")
df_evolucion = df.groupby("Fecha")["Score Total"].mean().reset_index()
fig_linea = px.line(df_evolucion, x="Fecha", y="Score Total", title="Score Total promedio por día", markers=True)
st.plotly_chart(fig_linea, use_container_width=True)

# Distribución de agentes sobre/bajo umbral de calidad
umbral = 80
df_agente = df.groupby("Agente")["Score Total"].mean().reset_index()
df_agente["Clasificación"] = df_agente["Score Total"].apply(lambda x: "Sobre umbral" if x >= umbral else "Bajo umbral")
fig_donut = px.pie(df_agente, names="Clasificación", title=f"Distribución de agentes según umbral {umbral}")
st.plotly_chart(fig_donut, use_container_width=True)
