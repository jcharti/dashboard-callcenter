# Panel de Análisis de Call Center

Este repositorio contiene un piloto de procesamiento de audios de un call center de ventas, con transcripción automática mediante Whisper y dashboards en Streamlit para análisis operativo y ejecutivo.

## 📂 Estructura del Proyecto

```bash
piloto_transcripcion/
├── audios/                      # Carpeta con archivos de audio de muestra
├── transcripciones/             # Salidas de transcripción (.txt)
├── pages/                       # Dashboards de Streamlit multipágina
│   ├── 1_🧑‍💼_Vista_Ejecutiva.py
│   ├── 2_🛠️_Vista_Operativa.py
│   └── 3_📊_Agentes.py          # Dashboard de ranking y detalle de agentes
├── app.py                       # Menú principal de Streamlit
├── transcriptor.py              # Script de procesamiento de audios y generación de resumen.csv
├── script_campana_bloques.csv   # Guiones comerciales por bloques
├── metadatos.csv                # Metadatos de cada audio (Archivo, Agente, Campaña, Fecha)
├── resumen.csv                  # Salida generada (indicadores por llamada)
├── deploy_cloud.sh              # Script para commit y push automático a GitHub
└── README.md                    # Documentación de este proyecto
```

## 🚀 Instalación y Entorno

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu_usuario/dashboard-callcenter.git
   cd dashboard-callcenter/piloto_transcripcion
   ```
2. Crea un entorno virtual e instala dependencias:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   > **Requisitos principales:**
   >
   > * `whisper` (OpenAI)
   > * `ffmpeg` (instálalo con `brew install ffmpeg` si usas macOS)
   > * `pandas`, `streamlit`, `plotly-express`, `tqdm`

## 🎯 Uso Local

1. **Procesar audios**:

   ```bash
   python transcriptor.py
   ```

   Esto genera:

   * `transcripciones/`: archivos `.txt` con cada transcripción
   * `resumen.csv`: indicadores y scoring por llamada
2. **Ejecutar dashboards**:

   ```bash
   streamlit run app.py
   ```

   Accede a las vistas ejecutivo, operativo y agentes desde el menú lateral.

## 📈 Publicación en Streamlit Cloud

1. Asegúrate de que tu repo esté actualizado en GitHub.
2. Ve a [Streamlit Cloud](https://streamlit.io/cloud) y crea una nueva app:

   * Conecta tu cuenta de GitHub
   * Selecciona este repositorio y `app.py`
3. Cada vez que hagas mejoras, ejecuta:

   ```bash
   ./deploy_cloud.sh
   ```

   Ingresa tu mensaje de commit y el script hará:

   * `git add .`
   * `git commit -m "tu mensaje"`
   * `git pull --rebase origin main`
   * `git push origin main`

## ⚙️ Flujo de Desarrollo

1. Actualiza `script_campana_bloques.csv` para nuevas campañas.
2. Coloca nuevos audios en `audios/` y actualiza `metadatos.csv`.
3. Ejecuta `python transcriptor.py` para regenerar `resumen.csv`.
4. Verifica localmente con `streamlit run app.py`.
5. Sube cambios con `./deploy_cloud.sh`.

## 💡 Buenas Prácticas

* Verifica que los nombres de campaña en `metadatos.csv` coincidan exactamente con los de `script_campana_bloques.csv`.
* Usa un subconjunto de audios livianos para demo en la nube.
* Revise la calidad de audio y ajusta el modelo Whisper (`small`, `medium`, `large`) según recursos.

---

¡Listo para analizar y demostrar tu piloto con datos reales y dashboards interactivos!
