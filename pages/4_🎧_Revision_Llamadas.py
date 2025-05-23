
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Revisión de Llamadas", layout="wide")
st.title("📄 Revisión de Llamadas")

# Cargar datos
csv_path = "resumen.csv"
csv_clasificacion = "clasificacion_llamadas.csv"

try:
    df = pd.read_csv(csv_path)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Archivo", "Agente", "Campaña", "Score Total"])

    # Inicializar archivo de clasificación si no existe
    if not os.path.exists(csv_clasificacion):
        clasificacion_df = pd.DataFrame(columns=["Archivo", "Clasificación", "Comentario"])
        clasificacion_df.to_csv(csv_clasificacion, index=False)

    clasificacion_df = pd.read_csv(csv_clasificacion)

    st.sidebar.header("🔎 Filtros")
    campañas = ["Todas"] + sorted(df["Campaña"].dropna().unique())
    agentes = ["Todos"] + sorted(df["Agente"].dropna().unique())
    campaña_sel = st.sidebar.selectbox("Campaña", campañas)
    agente_sel = st.sidebar.selectbox("Agente", agentes)
    score_range = st.sidebar.slider("Score Total", int(df["Score Total"].min()), int(df["Score Total"].max()), (60, 100))
    fechas = st.sidebar.date_input("Rango de fechas", [df["Fecha"].min(), df["Fecha"].max()])

    df_filtrado = df[
        (df["Fecha"] >= pd.to_datetime(fechas[0])) &
        (df["Fecha"] <= pd.to_datetime(fechas[1])) &
        (df["Score Total"] >= score_range[0]) &
        (df["Score Total"] <= score_range[1])
    ]

    if campaña_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Campaña"] == campaña_sel]
    if agente_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Agente"] == agente_sel]

    st.subheader("📋 Llamadas filtradas")
    st.dataframe(df_filtrado[["Archivo", "Fecha", "Agente", "Campaña", "Score Total", "Resultado Estimado"]], use_container_width=True)

    st.subheader("🎧 Revisión detallada")

    for _, row in df_filtrado.iterrows():
        with st.expander(f"{row['Agente']} | {row['Campaña']} | Score: {row['Score Total']} | {row['Archivo']}"):
            col1, col2 = st.columns([1, 4])
            with col1:
                audio_path = os.path.join("audios", row["Archivo"])
                if os.path.exists(audio_path):
                    st.audio(audio_path)
                else:
                    st.warning("Audio no disponible.")

            with col2:
                st.markdown("**Transcripción:**")
                st.markdown(row["Preview"])

                st.markdown("**Clasificación manual:**")
                clasificacion = st.radio(
                    f"Clasificar llamada {row['Archivo']}",
                    ["No clasificada", "Buena", "Mala", "Requiere coaching"],
                    index=0,
                    key=row["Archivo"]
                )
                comentario = st.text_input(f"Comentario para {row['Archivo']}", key=row["Archivo"] + "_c")

                if clasificacion != "No clasificada":
                    nuevo_registro = pd.DataFrame([{
                        "Archivo": row["Archivo"],
                        "Clasificación": clasificacion,
                        "Comentario": comentario
                    }])

                    clasificacion_df = clasificacion_df[clasificacion_df["Archivo"] != row["Archivo"]]
                    clasificacion_df = pd.concat([clasificacion_df, nuevo_registro], ignore_index=True)

    st.subheader("📤 Guardar clasificaciones")
    if st.button("💾 Guardar"):
        clasificacion_df.to_csv(csv_clasificacion, index=False)
        st.success("Clasificaciones guardadas correctamente.")

    st.download_button(
        label="⬇️ Exportar clasificaciones",
        data=clasificacion_df.to_csv(index=False).encode("utf-8"),
        file_name="clasificacion_llamadas.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error("❌ No se encontró el archivo resumen.csv. Ejecuta el transcriptor primero.")
