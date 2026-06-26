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
    st.subheader("🤖 Chat Legal Interactivo")
    
    # Inicializar historial
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    
    # Contenedor con scroll para el chat
    contenedor_chat = st.container(height=480, border=True)
    
    with contenedor_chat:
        for m in st.session_state.mensajes:
            with st.chat_message(m["rol"]):
                st.markdown(m["contenido"])
    
    # Botones de sugerencia rápida
    st.caption("💡 Sugerencias rápidas:")
    c1, c2, c3 = st.columns(3)
    prompt_sugerido = None
    
    if c1.button("⏱️ SLAs de PQR"): prompt_sugerido = "¿Cuáles son los tiempos máximos para PQR?"
    if c2.button("🔐 Datos Sensibles"): prompt_sugerido = "¿Controles para datos sensibles?"
    if c3.button("📝 Continuidad"): prompt_sugerido = "¿Reglas de continuidad del negocio?"
    
    # Input del chat
    prompt_usuario = st.chat_input("Escribe tu pregunta sobre RetailPro...")
    prompt_final = prompt_sugerido or prompt_usuario
    
    if prompt_final:
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_final})
        
        with contenedor_chat:
            with st.chat_message("user"):
                st.markdown(prompt_final)
            
            with st.chat_message("assistant"):
                with st.spinner("Consultando marco normativo..."):
                    try:
                        respuesta = model.generate_content(prompt_final)
                        texto = respuesta.text
                        st.markdown(texto)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": texto})
                    except Exception as e:
                        st.error(f"Error técnico: {e}")
        
        st.rerun()