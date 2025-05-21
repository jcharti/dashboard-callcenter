#!/bin/bash

echo "=============================="
echo "🚀 Iniciando procesamiento..."
echo "=============================="

# Cambia esta ruta si tu entorno virtual tiene otro nombre o ubicación
source ~/whisper-env/bin/activate || echo "⚠️ No se pudo activar el entorno, continúa igual..."

# Ejecutar el transcriptor
python3 transcriptor.py

echo ""
echo "✅ Transcripción finalizada."
echo "=============================="

# Verifica si streamlit está disponible
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit no está instalado. Ejecuta manualmente:"
    echo "   streamlit run app.py"
else
    echo "🚀 Ejecutando dashboard local..."
    streamlit run app.py
fi

