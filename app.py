import streamlit as st
import os
from pathlib import Path
import re
import google.generativeai as genai

st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide")

# Crear columnas
col1 = st.container()
col2 = st.container()

try:
    col1, col2 = st.columns([1, 1])
except Exception as e:
    st.error(f"Error creando columnas: {e}")

# Cargar CSS (sin usar __file__)
def aplicar_estilos():
    ruta_css = Path("estilos.css")
    if ruta_css.exists():
        st.markdown(f"<style>{ruta_css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

aplicar_estilos()

# Cargar y parsear marco legal con manejo de errores
def cargar_y_parsear_marco(ruta="marco_legal.txt"):
    try:
        p = Path(ruta)
        if not p.exists():
            return {"Aviso": "No se encontró marco_legal.txt"}
        contenido = p.read_text(encoding="utf-8")
        partes = re.split(r'(^# .+)', contenido, flags=re.MULTILINE)
        capitulos = {}
        for i in range(1, len(partes), 2):
            titulo = partes[i].replace('# ', '').strip()
            capitulos[titulo] = partes[i+1].strip()
        return capitulos or {"Aviso": "Archivo sin encabezados #"}
    except Exception as e:
        return {"Error": f"No se pudo leer/parcear el archivo: {e}"}

capitulos_dict = cargar_y_parsear_marco()

# Configurar API con variable de entorno y manejo de errores
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.warning(f"Fallo al configurar la API: {e}")
else:
    st.info("No hay GOOGLE_API_KEY en variables de entorno. El modelo no estará disponible.")

# Uso seguro de las columnas
with col1:
    st.subheader("📄 Marco Normativo")
    for titulo, contenido in capitulos_dict.items():
        with st.expander(titulo):
            st.markdown(contenido)

with col2:
    st.subheader("🤖 Chat Legal interactivo")
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    for m in st.session_state.mensajes:
        with st.chat_message(m["rol"]):
            st.markdown(m["contenido"])
    prompt = st.chat_input("Pregunta sobre RetailPro...")
    if prompt:
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        st.chat_message("assistant")
        st.markdown("Respuesta simulada (configura la API para respuestas reales).")
