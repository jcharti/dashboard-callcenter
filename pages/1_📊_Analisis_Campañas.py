
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Análisis de Campañas", layout="wide")
st.title("🔢 Análisis de Campañas")

csv_path = "resumen.csv"
if not os.path.exists(csv_path):
    st.error("❌ No se encontró el archivo resumen.csv.")
    st.stop()

df = pd.read_csv(csv_path)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df = df.dropna(subset=["Agente", "Campaña", "Fecha"])

st.sidebar.header("🎯 Filtros")
campañas_disponibles = ["Todas"] + sorted(df["Campaña"].dropna().unique())
campaña_sel = st.sidebar.selectbox("Selecciona una campaña", campañas_disponibles)
fechas = st.sidebar.date_input("Rango de fechas", [df["Fecha"].min(), df["Fecha"].max()])

if campaña_sel == "Todas":
    df_filtrado = df[(df["Fecha"] >= pd.to_datetime(fechas[0])) & (df["Fecha"] <= pd.to_datetime(fechas[1]))]
else:
    df_filtrado = df[(df["Campaña"] == campaña_sel) &
                     (df["Fecha"] >= pd.to_datetime(fechas[0])) &
                     (df["Fecha"] <= pd.to_datetime(fechas[1]))]

st.subheader(f"👥 Desempeño de agentes{' - Campaña: ' + campaña_sel if campaña_sel != 'Todas' else ''}")

def highlight_score(val):
    return "background-color: #d4edda" if isinstance(val, (int, float)) else ""

def icono_wpm(valor):
    if valor == "Adecuada":
        return "🟢 " + valor
    elif valor == "Lenta":
        return "🟡 " + valor
    elif valor == "Rápida":
        return "🔴 " + valor
    return valor

def icono_friccion(valor):
    if valor == "Baja":
        return "🟢 " + valor
    elif valor == "Media":
        return "🟡 " + valor
    elif valor == "Alta":
        return "🔴 " + valor
    return valor

ranking = df_filtrado.groupby("Agente").agg({
    "Score Total": "mean",
    "Apego al Guion (%)": "mean",
    "WPM": "mean",
    "Friccion (%)": "mean",
    "Archivo": "count",
    "Evaluación WPM": lambda x: x.mode().iloc[0] if not x.mode().empty else "",
    "Evaluación Fricción": lambda x: x.mode().iloc[0] if not x.mode().empty else "",
}).reset_index().round(0)

ranking = ranking.rename(columns={"Archivo": "Llamadas"})
ranking["Evaluación WPM"] = ranking["Evaluación WPM"].apply(icono_wpm)
ranking["Evaluación Fricción"] = ranking["Evaluación Fricción"].apply(icono_friccion)

tabla_ranking = ranking[[
    "Agente", "Llamadas", "Score Total", "Apego al Guion (%)",
    "WPM", "Evaluación WPM", "Friccion (%)", "Evaluación Fricción"
]].sort_values("Score Total", ascending=False)

tabla_ranking = tabla_ranking.style.format(precision=0).map(highlight_score, subset=["Score Total"])
st.dataframe(tabla_ranking, use_container_width=True)

st.subheader("📊 Cumplimiento por bloque de guión")
bloques = [c for c in df.columns if c.startswith("% ")]

df_bloques = df_filtrado[bloques].mean().round(1).reset_index()
df_bloques.columns = ["Bloque", "Cumplimiento (%)"]
df_bloques["Bloque"] = df_bloques["Bloque"].str.replace("% ", "")

fig_heat = px.bar(df_bloques, x="Bloque", y="Cumplimiento (%)",
                  title="Promedio de Cumplimiento por Bloque",
                  color="Cumplimiento (%)", color_continuous_scale="Tealgrn")
st.plotly_chart(fig_heat, use_container_width=True)

st.subheader("🌟 Llamadas destacadas")

df_filtrado["Evaluación WPM Icono"] = df_filtrado["Evaluación WPM"].apply(icono_wpm)
df_filtrado["Evaluación Fricción Icono"] = df_filtrado["Evaluación Fricción"].apply(icono_friccion)

top_mejores = df_filtrado.sort_values("Score Total", ascending=False).head(5)
top_peores = df_filtrado.sort_values("Score Total").head(5)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🟢 Mejores llamadas")
    st.dataframe(top_mejores[["Agente", "Score Total", "Evaluación WPM Icono", "Evaluación Fricción Icono"]])
with col2:
    st.markdown("### 🔴 Peores llamadas")
    st.dataframe(top_peores[["Agente", "Score Total", "Evaluación WPM Icono", "Evaluación Fricción Icono"]])
