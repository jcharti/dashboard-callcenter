import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_csv("resumen.csv")

st.set_page_config(page_title="Dashboard de Llamadas", layout="wide")
st.title("📞 Dashboard de Llamadas Transcritas")

# KPIs generales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total llamadas", len(df))
col2.metric("Duración promedio (min)", round(df["Duración (min)"].mean(), 2))
col3.metric("Palabras por minuto (avg)", round(df["Palabras/min"].mean(), 1))
col4.metric("Consentimientos afirmados", int(df["Respuesta Positiva"].sum()))

st.divider()

# Filtros
st.sidebar.title("Filtros")

filtro_objecion = st.sidebar.checkbox("Solo con objeción", False)
filtro_precio = st.sidebar.checkbox("Solo con mención de precio", False)
filtro_consentimiento = st.sidebar.checkbox("Solo si solicita consentimiento", False)
filtro_afirma_consentimiento = st.sidebar.checkbox("Solo si cliente dice 'sí'", False)

df_filtrado = df.copy()

if filtro_objecion:
    df_filtrado = df_filtrado[df_filtrado["Objeción Detectada"] == True]
if filtro_precio:
    df_filtrado = df_filtrado[df_filtrado["Mención Precio"] == True]
if filtro_consentimiento:
    df_filtrado = df_filtrado[df_filtrado["Solicita Consentimiento"] == True]
if filtro_afirma_consentimiento:
    df_filtrado = df_filtrado[df_filtrado["Respuesta Positiva"] == True]

# Visualización: tabla
st.subheader("📋 Llamadas")
st.dataframe(df_filtrado, use_container_width=True)

# Visualización: gráfico de barras de cantidad de palabras
st.subheader("📊 Palabras por llamada")
fig_bar = px.bar(
    df_filtrado,
    x="Archivo",
    y="Palabras",
    title="Cantidad de palabras por llamada",
    labels={"Archivo": "Llamada", "Palabras": "Cantidad de palabras"}
)
st.plotly_chart(fig_bar, use_container_width=True)

# Visualización: gráfico circular de consentimiento afirmado
st.subheader("✅ Consentimiento afirmado por cliente")
conteo = df["Respuesta Positiva"].value_counts().rename({True: "Sí", False: "No"})
fig_pie = px.pie(
    values=conteo.values,
    names=conteo.index,
    title="¿Cliente aceptó consentimiento?",
    color_discrete_sequence=["#2ecc71", "#e74c3c"]
)
st.plotly_chart(fig_pie, use_container_width=True)
