
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from datetime import datetime

st.title("🧑‍💼 Dashboard Ejecutivo - Análisis de Llamadas Call Center")

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

# Resumen ejecutivo
st.header("📌 Resumen Ejecutivo")
k1, k2, k3, k4 = st.columns(4)
k1.metric("📞 Llamadas Procesadas", len(df_filtrado))
k2.metric("🕒 Duración Promedio (min)", round(df_filtrado["Duración (min)"].mean(), 2))
k3.metric("❌ % con Objeción", f'{round(df_filtrado["Objeción Detectada"].mean() * 100, 1)} %')
k4.metric("✅ % Cierre Exitoso", f'{round((df_filtrado["Resultado Estimado"] == "Exitoso").mean() * 100, 1)} %')

st.divider()

# Comparativo por campaña
st.subheader("📈 Comparativo por Campaña")
campaña_group = df_filtrado.groupby("Campaña").agg({
    "Resultado Estimado": lambda x: (x == "Exitoso").mean() * 100,
    "Objeción Detectada": "mean"
}).reset_index()
campaña_group.rename(columns={
    "Resultado Estimado": "% Cierre Exitoso",
    "Objeción Detectada": "% con Objeción"
}, inplace=True)
if not campaña_group.empty:
    campaña_group["% Cierre Exitoso"] = pd.to_numeric(campaña_group["% Cierre Exitoso"], errors="coerce")
    campaña_group["% con Objeción"] = pd.to_numeric(campaña_group["% con Objeción"], errors="coerce")
    fig_cmp = px.bar(
        campaña_group,
        x="Campaña",
        y=["% Cierre Exitoso", "% con Objeción"],
        barmode="group",
        title="Desempeño Comercial por Campaña",
        text_auto=True
    )
    st.plotly_chart(fig_cmp, use_container_width=True)
else:
    st.info("No hay datos disponibles para mostrar comparación por campaña.")

# Ranking de agentes
st.subheader("🏆 Ranking de Agentes por % de Éxito")
agente_group = df_filtrado.groupby("Agente").agg({
    "Resultado Estimado": lambda x: (x == "Exitoso").mean() * 100,
    "Archivo": "count"
}).rename(columns={"Resultado Estimado": "% Cierre Exitoso", "Archivo": "Llamadas"}).sort_values(by="% Cierre Exitoso", ascending=False).reset_index()
st.dataframe(agente_group, use_container_width=True)

# Tendencia temporal de éxito
st.subheader("📅 Tendencia de Llamadas Exitosas")
df_fecha = df_filtrado.copy()
df_fecha["Fecha"] = df_fecha["Fecha"].dt.date
grafico_tendencia = df_fecha.groupby("Fecha")["Resultado Estimado"].apply(lambda x: (x == "Exitoso").mean() * 100).reset_index(name="% Exitosas")
fig_line = px.line(grafico_tendencia, x="Fecha", y="% Exitosas", markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# Descargar CSV
st.subheader("⬇️ Exportar Datos Filtrados")
csv_buffer = StringIO()
df_filtrado.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 Descargar CSV",
    data=csv_buffer.getvalue(),
    file_name="resumen_filtrado.csv",
    mime="text/csv"
)

# Tabla
st.subheader("📋 Detalle de Llamadas Filtradas")
st.dataframe(
    df_filtrado[[
        "Fecha", "Archivo", "Agente", "Campaña",
        "Duración (min)", "Palabras", "Palabras/min",
        "Cierre Detectado", "Objeción Detectada",
        "Consentimiento Solicitado", "Consentimiento Afirmado",
        "Precio Mencionado", "Saludo Detectado",
        "Resultado Estimado", "Preview"
    ]].sort_values(by="Fecha", ascending=False),
    use_container_width=True
)

# Cierre ejecutivo
st.subheader("🧠 Conclusión Ejecutiva")
exitosas = (df_filtrado["Resultado Estimado"] == "Exitoso").sum()
total = len(df_filtrado)
consentimientos = df_filtrado["Consentimiento Afirmado"].sum()

if not campaña_group.empty:
    mejor_campaña = campaña_group.sort_values(by="% Cierre Exitoso", ascending=False).iloc[0]
    mejor_nombre = mejor_campaña["Campaña"]
    mejor_cierre = round(mejor_campaña["% Cierre Exitoso"], 1)
else:
    mejor_nombre = "-"
    mejor_cierre = 0

st.markdown(
    f"""
- Se analizaron **{total} llamadas** dentro del período y filtros seleccionados.
- El **{round((exitosas / total) * 100, 1)}%** fueron marcadas como *exitosas* (cierre sin objeción).
- El **{round((consentimientos / total) * 100, 1)}%** de las llamadas tuvo **consentimiento afirmado**.
- La campaña con mejor desempeño es **{mejor_nombre}** con **{mejor_cierre}% de cierres exitosos**.
- Recomendación: **enfocar entrenamiento comercial** en campañas o agentes con alta tasa de objeciones y baja conversión.
""")

st.caption("🔍 Dashboard preparado para decisión comercial ejecutiva.")
