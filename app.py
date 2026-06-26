import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide")

# --- CARGA DE ESTILOS CSS PROFESIONAL ---
def aplicar_estilos():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(directorio_actual, "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

aplicar_estilos()

# --- CONFIGURACIÓN DE IA ---
GOOGLE_API_KEY = "AIzaSyB1H--nWeVqnTninyrYSRrftA5bI2gnGr8"
genai.configure(api_key=GOOGLE_API_KEY)

# Carga de contexto para RAG
def cargar_marco():
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Marco normativo no disponible."

documento = cargar_marco()
instrucciones = f"Eres el Asistente Ejecutivo de RetailPro. Marco normativo: {documento}. Responde basado estrictamente en este documento."
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instrucciones)

# --- INTERFAZ ---
st.title("⚖️ Asistente de Gobernanza RetailPro")
col1, col2 = st.columns([1, 1])

# COLUMNA 1: Marco Normativo con Acordeones (Expander)
with col1:
    st.subheader("📄 Marco Normativo")
    with st.container(height=600, border=True):
        st.markdown("### 📜 Referencias")
        st.write("RetailPro adopta como base la legislación comercial, laboral, protección de datos y marcos internacionales como ISO/IEC 27001 y NIST.")
        
        st.markdown("### 📋 Definiciones Corporativas")
        with st.expander("Gobierno corporativo"):
            st.write("Sistema mediante el cual las empresas son dirigidas y controladas.")
        with st.expander("Riesgo"):
            st.write("Efecto de la incertidumbre sobre los objetivos de la organización.")
        with st.expander("Control"):
            st.write("Medidas adoptadas para mitigar riesgos y asegurar el cumplimiento.")
        with st.expander("Activo de información"):
            st.write("Información que tiene valor para la organización y debe ser protegida.")

# COLUMNA 2: Chat Interactivo
with col2:
    st.subheader("🤖 Chat Legal interactivo")
    contenedor_chat = st.container(height=480, border=True)
    
    if "mensajes" not in st.session_state: 
        st.session_state.mensajes = []
        
    with contenedor_chat:
        for m in st.session_state.mensajes:
            with st.chat_message(m["rol"]): 
                st.markdown(m["contenido"])
    
    # Sugerencias rápidas
    st.caption("💡 Sugerencias:")
    c1, c2, c3 = st.columns(3)
    prompt_sugerido = None
    
    if c1.button("⏱️ SLAs PQR"): prompt_sugerido = "¿Tiempos máximos para PQR?"
    if c2.button("🔐 Datos"): prompt_sugerido = "¿Controles para datos sensibles?"
    if c3.button("📝 Continuidad"): prompt_sugerido = "¿Reglas de continuidad?"
    
    prompt_usuario = st.chat_input("Pregunta sobre RetailPro...")
    prompt_final = prompt_sugerido or prompt_usuario
    
    if prompt_final:
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_final})
        with contenedor_chat:
            with st.chat_message("user"): st.markdown(prompt_final)
            with st.chat_message("assistant"):
                with st.spinner("Analizando..."):
                    try:
                        respuesta = model.generate_content(prompt_final)
                        texto = respuesta.text
                        st.markdown(texto)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": texto})
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.rerun()