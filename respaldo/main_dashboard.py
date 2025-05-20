import streamlit as st

st.set_page_config(page_title="Panel de Llamadas - Call Center", layout="wide")
st.sidebar.title("🧭 Navegación")
vista = st.sidebar.radio("Selecciona una vista:", ["🧑‍💼 Ejecutiva", "🛠️ Operativa"])

if vista == "🧑‍💼 Ejecutiva":
    exec(open("dashboard_ejecutivo.py").read())
elif vista == "🛠️ Operativa":
    exec(open("dashboard_operativo.py").read())
