
import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

st.set_page_config(page_title="Gestión de Metadatos de Llamadas", layout="wide")
st.title("🗃️ Gestión de Metadatos de Llamadas")

METADATOS_PATH = "metadatos.xlsx"
HOJA = "Metadatos"

if not os.path.exists(METADATOS_PATH):
    df_vacio = pd.DataFrame(columns=[
        "ID", "Archivo", "Ruta Audio", "Agente", "Campaña", "Fecha Llamada", "Estado",
        "Fecha Procesado", "Usuario Editor", "Notas", "KPI Score", "created_at", "updated_at", "Motivo Rechazo"
    ])
    with pd.ExcelWriter(METADATOS_PATH, engine="openpyxl") as writer:
        df_vacio.to_excel(writer, index=False, sheet_name=HOJA)

df = pd.read_excel(METADATOS_PATH, sheet_name=HOJA)
st.subheader("📜 Historial de metadatos existentes")

if not df.empty:
    campañas = sorted(df["Campaña"].dropna().unique().tolist())
    filtro = st.selectbox("🔎 Filtrar por campaña", options=["Todas"] + campañas)
    df_filtrado = df if filtro == "Todas" else df[df["Campaña"] == filtro]
    st.dataframe(df_filtrado)
else:
    st.info("No hay registros previos.")

st.subheader("📥 Descargar plantilla para carga nueva")

if not os.path.exists("audios"):
    os.makedirs("audios")

archivos_audio = [f for f in os.listdir("audios") if f.endswith((".mp3", ".wav", ".m4a"))]
plantilla = pd.DataFrame({
    "ID": ["" for _ in archivos_audio],
    "Archivo": archivos_audio,
    "Ruta Audio": ["" for _ in archivos_audio],
    "Agente": ["" for _ in archivos_audio],
    "Campaña": ["" for _ in archivos_audio],
    "Fecha Llamada": ["" for _ in archivos_audio],
    "Estado": ["Pendiente" for _ in archivos_audio],
    "Fecha Procesado": ["" for _ in archivos_audio],
    "Usuario Editor": ["" for _ in archivos_audio],
    "Notas": ["" for _ in archivos_audio],
    "KPI Score": ["" for _ in archivos_audio],
    "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in archivos_audio],
    "updated_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in archivos_audio],
    "Motivo Rechazo": ["" for _ in archivos_audio]
})
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    plantilla.to_excel(writer, index=False, sheet_name="Plantilla")
st.download_button("📄 Descargar plantilla Excel", data=output.getvalue(), file_name="plantilla_metadatos_llamadas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.subheader("📤 Subir nueva carga de metadatos")
archivo_subido = st.file_uploader("Selecciona un archivo Excel con nuevos metadatos", type=["xlsx"])

if archivo_subido:
    nuevos = pd.read_excel(archivo_subido)
    st.write("Vista previa de nuevos registros:")
    st.dataframe(nuevos)

    campos_requeridos = ["Archivo", "Agente", "Campaña", "Fecha Llamada"]

    def validar_fecha_flexible(valor):
        if isinstance(valor, datetime):
            return True
        try:
            if isinstance(valor, float) or isinstance(valor, int):
                return True
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    datetime.strptime(str(valor), fmt)
                    return True
                except:
                    continue
        except:
            pass
        return False

    def validar_fila_y_motivo(fila):
        for campo in campos_requeridos:
            if pd.isna(fila[campo]) or str(fila[campo]).strip() == "":
                return False, f"Campo obligatorio vacío: {campo}"
        if not validar_fecha_flexible(fila["Fecha Llamada"]):
            return False, "Formato de fecha inválido o no reconocido"
        return True, ""

    nuevos["Es Valido"], nuevos["Motivo Rechazo"] = zip(*nuevos.apply(validar_fila_y_motivo, axis=1))
    validos = nuevos[nuevos["Es Valido"]].copy()
    rechazados = nuevos[~nuevos["Es Valido"]].copy()

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    validos["Estado"] = "Pendiente"
    validos["created_at"] = ahora
    validos["updated_at"] = ahora
    validos["ID"] = [f"row_{i}_{int(datetime.now().timestamp())}" for i in range(len(validos))]

    rechazados["Estado"] = "Rechazado"
    rechazados["created_at"] = ahora
    rechazados["updated_at"] = ahora
    rechazados["ID"] = [f"row_r_{i}_{int(datetime.now().timestamp())}" for i in range(len(rechazados))]

    archivos_existentes = df["Archivo"].dropna().unique()
    validos = validos[~validos["Archivo"].isin(archivos_existentes)]

    df_actualizado = pd.concat([df, validos, rechazados], ignore_index=True)
    with pd.ExcelWriter(METADATOS_PATH, engine="openpyxl") as writer:
        df_actualizado.to_excel(writer, index=False, sheet_name=HOJA)

    st.success(f"✅ Se agregaron {len(validos)} registros válidos y {len(rechazados)} rechazados.")
    if not rechazados.empty:
        st.subheader("❌ Registros rechazados")
        st.dataframe(rechazados)
