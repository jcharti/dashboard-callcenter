import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Ranking de Agentes", layout="wide")
st.title("📊 Dashboard de Agentes")

# ========== 1. Mostrar Script de la Campaña por Bloques ==========
# Cargar script base
try:
    script_df = pd.read_csv("script_campana_bloques.csv")
except Exception as e:
    st.warning(f"No se pudo cargar el guion: {e}")
    script_df = pd.DataFrame()

if not script_df.empty:
    campañas_script = script_df["Campaña"].unique().tolist()
    campaña_sel = st.selectbox("Selecciona campaña para ver el guion:", campañas_script)
    script_row = script_df[script_df["Campaña"] == campaña_sel].iloc[0]

    st.subheader(f"📑 Guión comercial por bloques - Campaña: {campaña_sel}")
    for bloque in ["Saludo", "Presentación", "Oferta", "Beneficios", "Cierre"]:
        st.markdown(f"**{bloque}:**")
        st.info(str(script_row.get(bloque, "")))
else:
    st.warning("No hay script disponible para mostrar los bloques de la campaña.")

# ========== 2. Resto del dashboard de agentes ==========

# Cargar resumen
try:
    df = pd.read_csv("resumen.csv", parse_dates=["Fecha"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
except Exception as e:
    st.error(f"Error al cargar resumen.csv: {e}")
    st.stop()

# KPI + Score (últimos 30 días)
ultimo_mes = df[df["Fecha"] >= (df["Fecha"].max() - pd.Timedelta(days=30))]

ranking = (
    ultimo_mes.groupby("Agente").agg({
        "Score Total": "mean",
        "Apego al Guion (%)": "mean",
        "Archivo": "count",
        "% Saludo": "mean",
        "% Presentación": "mean",
        "% Oferta": "mean",
        "% Beneficios": "mean",
        "% Cierre": "mean"
    })
    .rename(columns={"Archivo": "Llamadas"})
    .reset_index()
)

# Redondear sin decimales
ranking = ranking.round(0).astype({
    "Llamadas": int,
    "Score Total": int,
    "Apego al Guion (%)": int,
    "% Saludo": int,
    "% Presentación": int,
    "% Oferta": int,
    "% Beneficios": int,
    "% Cierre": int
})

# Estilo de score
def highlight_score(val):
    return "background-color: #d4edda" if isinstance(val, (int, float)) else ""

# Mostrar tabla
st.subheader("🏅 Ranking de Agentes (últimos 30 días)")
st.caption("Valores redondeados sin decimales. Score resaltado en verde.")
tabla_ranking = ranking[[
    "Agente", "Llamadas", "Score Total", "Apego al Guion (%)",
    "% Saludo", "% Presentación", "% Oferta", "% Beneficios", "% Cierre"
]]
tabla_ranking = tabla_ranking.style.map(highlight_score, subset=["Score Total"])
st.dataframe(tabla_ranking, use_container_width=True)

# Selector de agente
agente_sel = st.selectbox("Selecciona un agente para ver el detalle:", ranking["Agente"].tolist())

# Detalle de llamadas
st.subheader(f"📂 Detalle de llamadas del agente {agente_sel}")
df_agente_llamadas = df[df["Agente"] == agente_sel].sort_values(by="Fecha", ascending=False)

for idx, fila in df_agente_llamadas.iterrows():
    with st.expander(f"{fila['Fecha'].date()} - {fila['Archivo']}"):
        st.markdown(f"**Campaña:** {fila['Campaña']}")
        st.markdown(f"**Preview:** {fila['Preview']}")
        
        # Reproductor de audio
        audio_path = f"audios/{fila['Archivo']}"
        if os.path.exists(audio_path):
            st.audio(audio_path)
        else:
            st.warning("Audio no encontrado.")

        # Mostrar transcripción
        txt_path = f"transcripciones/{fila['Archivo'].replace('.mp3', '.txt')}"
        try:
            with open(txt_path, "r", encoding="utf-8") as t:
                contenido = t.read()
            st.text_area("📝 Transcripción completa:", value=contenido, height=200, key=f"txt_{fila['Archivo']}")
        except FileNotFoundError:
            st.warning("⚠️ Transcripción no encontrada.")

# Gráfico de evolución
df_agente = df[df["Agente"] == agente_sel].copy()
score_tiempo = df_agente.groupby("Fecha")["Score Total"].mean().reset_index()

st.subheader(f"📈 Evolución del Score - {agente_sel}")
fig_line = px.line(score_tiempo, x="Fecha", y="Score Total", markers=True)
fig_line.update_layout(yaxis_title="Score", xaxis_title="Fecha")
st.plotly_chart(fig_line, use_container_width=True)
