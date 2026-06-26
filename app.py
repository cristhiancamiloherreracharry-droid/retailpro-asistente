import streamlit as st
import google.generativeai as genai
import os
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide")

# --- CARGA DE ESTILOS CSS ---
def aplicar_estilos():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(directorio_actual, "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

aplicar_estilos()

# --- CONFIGURACIÓN DE IA ---
# Usa tu clave API activa
GOOGLE_API_KEY = "AIzaSyB1H--nWeVqnTninyrYSRrftA5bI2gnGr8"
genai.configure(api_key=GOOGLE_API_KEY)

def cargar_y_parsear_marco():
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
        # Divide el contenido usando títulos Markdown empezando con #
        partes = re.split(r'(^# .+)', contenido, flags=re.MULTILINE)
        capitulos = {}
        for i in range(1, len(partes), 2):
            titulo = partes[i].replace('# ', '').strip()
            contenido_cap = partes[i+1].strip()
            capitulos[titulo] = contenido_cap
        return capitulos
    except:
        return {"Error": "No se pudo cargar el marco legal. Verifica el archivo .txt"}

capitulos_dict = cargar_y_parsear_marco()
documento_completo = "\n".join([f"{t}\n{c}" for t, c in capitulos_dict.items()])

# --- LÓGICA IA ---
instrucciones = f"Eres el Asistente Ejecutivo de RetailPro. Marco normativo: {documento_completo}. Responde basado estrictamente en este documento."
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instrucciones)

# --- UI (EL ORDEN AQUÍ ES CRÍTICO) ---
st.title("⚖️ Asistente de Gobernanza RetailPro")

# 1. Definir columnas PRIMERO
col1, col2 = st.columns([1, 1])

# 2. USAR COLUMNAS (ahora col1 y col2 ya existen en memoria)
with col1:
    st.subheader("📄 Marco Normativo")
    with st.container(height=600, border=True):
        for titulo, contenido in capitulos_dict.items():
            with st.expander(titulo):
                st.markdown(contenido)

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
                with st.spinner("Analizando marco..."):
                    try:
                        respuesta = model.generate_content(prompt_final)
                        texto = respuesta.text
                        st.markdown(texto)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": texto})
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.rerun()