import streamlit as st
import os
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Legal RetailPro", layout="wide")

# --- CARGA DE ESTILOS CSS ---
def aplicar_estilos():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(directorio_actual, "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Archivo de estilos no encontrado en: {ruta_css}")

aplicar_estilos()

# --- CONFIGURACIÓN DE IA (Reemplaza con tu API Key) ---
GOOGLE_API_KEY = "TU_API_KEY_AQUI"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- LÓGICA DE LA APP ---
# Layout de dos columnas
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🏛️ Marco Normativo")
    # Aquí puedes cargar tu archivo de texto o poner el contenido directo
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.error("Archivo 'marco_legal.txt' no encontrado.")

with col2:
    st.subheader("🤖 Chat Legal")
    
    # 1. Renderizar historial
    if "mensajes" not in st.session_state: 
        st.session_state.mensajes = []
        
    for m in st.session_state.mensajes:
        with st.chat_message(m["rol"]): 
            st.markdown(m["contenido"])
    
    # 2. Capturar input
    prompt = st.chat_input("Consulta aquí:")
    if prompt:
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)
        
        # 3. Llamado a la IA con control de estado y spinner
        with st.chat_message("assistant"):
            with st.spinner("Conectando con el motor cognitivo..."):
                try:
                    respuesta = model.generate_content(prompt)
                    
                    # Validar si la IA devolvió una respuesta vacía o fue bloqueada
                    if not respuesta.parts:
                        st.error("La IA bloqueó la respuesta por sus filtros de seguridad internos.")
                    else:
                        texto = respuesta.text
                        st.markdown(texto)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": texto})
                        
                except Exception as e:
                    # Forzamos la impresión del error exacto en la UI
                    st.error(f"Falla en la API: {type(e).__name__} - {e}")
