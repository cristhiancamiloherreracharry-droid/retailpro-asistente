import streamlit as st
import google.generativeai as genai
import os
import re
from pathlib import Path

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide")

# --- CARGA DE ESTILOS CSS (sin __file__) ---
def aplicar_estilos():
    ruta_css = Path("estilos.css")
    if ruta_css.exists():
        with ruta_css.open("r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

aplicar_estilos()

# --- CONFIGURACIÓN DE IA (usar variable de entorno) ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    st.warning("No se encontró la variable de entorno GOOGLE_API_KEY. Define la variable para usar la IA.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"Error configurando la API de Google: {e}")

# --- CARGA Y PARSEO DEL MARCO LEGAL ---
def cargar_y_parsear_marco(ruta="marco_legal.txt"):
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        return {"Aviso": "No se encontró el archivo marco_legal.txt"}
    try:
        contenido = ruta_path.read_text(encoding="utf-8")
        partes = re.split(r'(^# .+)', contenido, flags=re.MULTILINE)
        capitulos = {}
        for i in range(1, len(partes), 2):
            titulo = partes[i].replace('# ', '').strip()
            contenido_cap = partes[i+1].strip()
            capitulos[titulo] = contenido_cap
        if not capitulos:
            return {"Aviso": "El archivo está vacío o no contiene encabezados con #"}
        return capitulos
    except Exception as e:
        return {"Error": f"No se pudo cargar o parsear el marco legal: {e}"}

capitulos_dict = cargar_y_parsear_marco()
documento_completo = "\n".join([f"{t}\n{c}" for t, c in capitulos_dict.items()])

# --- LÓGICA IA (solo si API configurada) ---
instrucciones = (
    "Eres el Asistente Ejecutivo de RetailPro. "
    f"Marco normativo: {documento_completo}. "
    "Responde basado estrictamente en este documento."
)

model = None
if GOOGLE_API_KEY:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instrucciones)
    except Exception as e:
        st.error(f"No se pudo inicializar el modelo: {e}")

# --- UI ---
st.title("⚖️ Asistente de Gobernanza RetailPro")

# Crear columnas antes de usarlas y con manejo de excepción
try:
    col1, col2 = st.columns([1, 1])
except Exception as e:
    st.error(f"Error creando columnas: {e}")
    # Fallback: usar una sola columna para que la app no rompa
    col1 = st.container()
    col2 = st.container()

# --- COLUMNA 1: Marco Normativo ---
with col1:
    st.subheader("📄 Marco Normativo")
    for titulo, contenido in capitulos_dict.items():
        with st.expander(titulo):
            st.markdown(contenido)

# --- COLUMNA 2: Chat ---
with col2:
    st.subheader("🤖 Chat Legal interactivo")

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Mostrar historial
    for m in st.session_state.mensajes:
        with st.chat_message(m["rol"]):
            st.markdown(m["contenido"])

    st.caption("💡 Sugerencias:")
    c1, c2, c3 = st.columns(3)
    prompt_sugerido = None
    if c1.button("⏱️ SLAs PQR"):
        prompt_sugerido = "¿Tiempos máximos para PQR?"
    if c2.button("🔐 Datos"):
        prompt_sugerido = "¿Controles para datos sensibles?"
    if c3.button("📝 Continuidad"):
        prompt_sugerido = "¿Reglas de continuidad?"

    prompt_usuario = st.chat_input("Pregunta sobre RetailPro...")
    prompt_final = prompt_sugerido or prompt_usuario

    if prompt_final:
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_final})
        with st.chat_message("assistant"):
            with st.spinner("Analizando marco..."):
                if model is None:
                    texto = "El modelo no está disponible. Verifica la configuración de la API."
                else:
                    try:
                        respuesta = model.generate_content(prompt_final)
                        texto = getattr(respuesta, "text", str(respuesta))
                    except Exception as e:
                        texto = f"Error al generar respuesta: {e}"
                st.markdown(texto)
                st.session_state.mensajes.append({"rol": "assistant", "contenido": texto})
        # Evitar rerun innecesario; solo usar si realmente lo necesitas
        # st.experimental_rerun()
