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
        "Archivo": "count",
        "Score Total": "mean",
        "Apego al Guion (%)": "mean",
        "WPM": "mean",
        "Friccion (%)": "mean"
    }).rename(columns={"Archivo": "Llamadas"}).reset_index()
)

ranking["Evaluación WPM"] = ranking["WPM"].apply(lambda x: "Lenta" if x < 90 else "Adecuada" if x <= 140 else "Rápida")
ranking["Evaluación Fricción"] = ranking["Friccion (%)"].apply(lambda x: "Baja" if x <= 5 else "Media" if x <= 15 else "Alta")


def icono_wpm(valor):
    if valor == "Adecuada":
        return "🟢 Adecuada"
    elif valor == "Lenta":
        return "🟠 Lenta"
    else:
        return "🔴 Rápida"

ranking["Evaluación WPM"] = ranking["Evaluación WPM"].apply(icono_wpm)

def icono_friccion(valor):
    if valor == "Baja":
        return "🟢 Baja"
    elif valor == "Media":
        return "🟠 Media"
    else:
        return "🔴 Alta"

ranking["Evaluación Fricción"] = ranking["Evaluación Fricción"].apply(icono_friccion)






if st.button("ℹ️ Ver explicación de KPIs y Score"):
    st.switch_page("pages/explicacion_score.py")

# Redondear sin decimales
ranking = ranking.round(0).astype({
    "Llamadas": int,
    "Score Total": int,
    "Apego al Guion (%)": int,
    "WPM": int,
    "Friccion (%)": int
})


# Estilo de score
def highlight_score(val):
    return "background-color: #d4edda" if isinstance(val, (int, float)) else ""

# Mostrar tabla
st.subheader("🏅 Ranking de Agentes (últimos 30 días)")
st.caption("Valores redondeados sin decimales. Score resaltado en verde.")
tabla_ranking = ranking[[
    "Agente", "Llamadas", "Score Total", "Apego al Guion (%)",
    "WPM", "Evaluación WPM", "Friccion (%)", "Evaluación Fricción"
]].sort_values("Score Total", ascending=False)
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



st.subheader("📊 Comparación de Score Total por Agente")

fig = px.bar(
    ranking,
    x="Agente",
    y="Score Total",
    text="Score Total",
    color="Score Total",
    color_continuous_scale="Blues",
    title="Score Total Promedio por Agente en los Últimos 30 Días"
)
fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig, use_container_width=True)
