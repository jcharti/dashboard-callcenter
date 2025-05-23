import os

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mi Desempeño", layout="wide")
st.title("👤 Mi Desempeño como Agente")

st.markdown("Esta sección permite visualizar tu evolución personal de desempeño en el tiempo.")

# Cargar datos de resumen
csv_path = "resumen.csv"
try:
    df = pd.read_csv(csv_path)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Agente", "Fecha"])

    agentes = sorted(df["Agente"].dropna().unique())
    agente_sel = st.selectbox("Selecciona tu nombre", agentes)

    df_agente = df[df["Agente"] == agente_sel]

    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("📊 Desempeño general de " + agente_sel)
    with col2:
        st.link_button("ℹ️ ¿Cómo se calcula el score?", "https://tu-app.com/pages/Explicacion_Score")

    # Tabla con estilo personalizado
    def highlight_score(val):
        return "background-color: #d4edda" if isinstance(val, (int, float)) else ""

    st.caption("Valores redondeados sin decimales. Score resaltado en verde.")

    ranking = df.groupby("Agente").agg({
        "Score Total": "mean",
        "Apego al Guion (%)": "mean",
        "WPM": "mean",
        "Friccion (%)": "mean",
        "Archivo": "count",
        "Evaluación WPM": lambda x: x.mode().iloc[0] if not x.mode().empty else "",
        "Evaluación Fricción": lambda x: x.mode().iloc[0] if not x.mode().empty else "",
    }).reset_index().round(0)

    ranking = ranking.rename(columns={"Archivo": "Llamadas"})

    # Añadir íconos de colores
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

    ranking["Evaluación WPM"] = ranking["Evaluación WPM"].apply(icono_wpm)
    ranking["Evaluación Fricción"] = ranking["Evaluación Fricción"].apply(icono_friccion)

    tabla_ranking = ranking[[
        "Agente", "Llamadas", "Score Total", "Apego al Guion (%)",
        "WPM", "Evaluación WPM", "Friccion (%)", "Evaluación Fricción"
    ]].sort_values("Score Total", ascending=False)

    tabla_ranking = tabla_ranking.style.format(precision=0).map(highlight_score, subset=["Score Total"])
    st.dataframe(tabla_ranking, use_container_width=True)

    st.subheader("📈 Evolución de mi Score Total")

    df_evolucion = df_agente.groupby("Fecha")["Score Total"].mean().reset_index()
    fig = px.line(df_evolucion, x="Fecha", y="Score Total",
                  markers=True,
                  title="Evolución diaria del Score Total",
                  labels={"Score Total": "Score"},
                  height=300)
    fig.update_traces(line=dict(color="royalblue"))
    st.plotly_chart(fig, use_container_width=True)



    
    st.subheader("🎧 Mis llamadas destacadas")

    def mostrar_llamadas_detalle(df_llamadas, titulo):
        st.markdown(f"### {titulo}")
        for _, row in df_llamadas.iterrows():
            with st.expander(f"🎧 Score: {row['Score Total']}"):
                col1, col2 = st.columns([1, 4])
                with col1:
                    audio_path = os.path.join("audios", row["Archivo"])
                    if os.path.exists(audio_path):
                        st.audio(audio_path)
                    else:
                        st.warning("Audio no disponible.")
                with col2:
                    st.markdown("**Transcripción completa:**")
                    st.text(row.get("Transcripción", row.get("Preview", "Sin transcripción disponible.")))

    top_mejores = df_agente.sort_values("Score Total", ascending=False).head(3)
    top_peores = df_agente.sort_values("Score Total").head(3)

    col1, col2 = st.columns(2)
    with col1:
        mostrar_llamadas_detalle(top_mejores, "🟢 Mis mejores llamadas")
    with col2:
        mostrar_llamadas_detalle(top_peores, "🔴 Mis llamadas con oportunidad de mejora")
    


except FileNotFoundError:
    st.error("❌ No se encontró el archivo resumen.csv.")



st.subheader("🌟 Mis llamadas destacadas")

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

df["Evaluación WPM Icono"] = df["Evaluación WPM"].apply(icono_wpm)
df["Evaluación Fricción Icono"] = df["Evaluación Fricción"].apply(icono_friccion)

df_agente = df[df["Agente"] == agente_sel]

top_mejores = df_agente.sort_values("Score Total", ascending=False).head(3)
top_peores = df_agente.sort_values("Score Total").head(3)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🟢 Mis mejores llamadas")
    st.dataframe(top_mejores[["Fecha", "Score Total", "Evaluación WPM Icono", "Evaluación Fricción Icono"]])
with col2:
    st.markdown("### 🔴 Mis llamadas con oportunidad de mejora")
    st.dataframe(top_peores[["Fecha", "Score Total", "Evaluación WPM Icono", "Evaluación Fricción Icono"]])
