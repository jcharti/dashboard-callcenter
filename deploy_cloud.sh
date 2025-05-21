#!/bin/bash

echo "Guardando todos los cambios locales..."
git add .

echo "¿Qué mensaje deseas para el commit?"
read mensaje

git commit -m "$mensaje"

echo "Actualizando rama principal en remoto..."
git pull --rebase origin main
git push origin main

echo "✅ Cambios subidos. Ahora tu Streamlit Cloud actualizará la app."
