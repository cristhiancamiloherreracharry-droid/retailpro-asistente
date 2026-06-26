import streamlit as st
import os
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RetailPro - Asistente Legal", layout="wide", page_icon="⚖️")

# --- CONFIGURACIÓN DE IA ---
# Agrega tu API KEY aquí
GOOGLE_API_KEY = "TU_API_KEY_AQUI" 
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FUNCIONES DE CARGA ---
def cargar_documento():
    ruta = os.path.join(os.path.dirname(__file__), "marco_legal.txt")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    return "Error: No se encontró el archivo 'marco_legal.txt'"

def aplicar_estilos():
    ruta_css = os.path.join(os.path.dirname(__file__), "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargamos el contenido una sola vez
texto_normativo = cargar_documento()

# --- INTERFAZ ---
aplicar_estilos()

# Header Superior
st.markdown("""
    <div class="main-header">
        <img src="https://cdn-icons-png.flaticon.com/512/584/584611.png" width="40" style="margin-right:15px">
        <div style="font-size: 24px; font-weight: 700; color: #1E293B;">RetailPro <span style="font-weight:400; font-size:16px; color:#64748B;">| Asistente Legal Interactivo</span></div>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

# --- COLUMNA 1: MARCO NORMATIVO (DINÁMICO) ---
with col1:
    st.markdown('<div class="card-header-blue">📘 Marco Normativo</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Mostramos el contenido del TXT
        # Usamos un área con scroll para que no se haga infinita la página
        st.markdown(f"""
            <div style="height: 550px; overflow-y: auto; padding-right: 10px; font-size: 0.95rem; line-height: 1.6;">
                {texto_normativo}
            </div>
        """, unsafe_allow_html=True)

# --- COLUMNA 2: CHAT INTERACTIVO ---
with col2:
    st.markdown('<div class="card-header-purple">💬 Chat Legal Interactivo</div>', unsafe_allow_html=True)
    
    tab_chat, tab_slas, tab_datos = st.tabs(["💬 Chat", "📋 SLAs de PQR", "🗄️ Datos Sensibles"])
    
    with tab_chat:
        # Historial de chat
        if "mensajes" not in st.session_state:
            st.session_state.mensajes = [
                {"rol": "assistant", "contenido": "¡Hola! Soy tu asistente legal de RetailPro. He analizado el Marco Normativo. ¿En qué puedo ayudarte hoy?"}
            ]

        contenedor_chat = st.container(height=400)
        
        with contenedor_chat:
            for m in st.session_state.mensajes:
                with st.chat_message(m["rol"]):
                    st.markdown(m["contenido"])

        # Input de usuario
        if prompt := st.chat_input("Escribe tu pregunta sobre RetailPro..."):
            # Mostrar mensaje del usuario
            st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
            with contenedor_chat:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Respuesta de la IA
            with contenedor_chat:
                with st.chat_message("assistant"):
                    with st.spinner("Consultando normativa..."):
                        # Instrucción de sistema + Contexto del archivo + Pregunta
                        prompt_sistema = f"""
                        Eres un asistente legal experto de RetailPro. 
                        Tu base de conocimientos es el siguiente texto:
                        
                        {texto_normativo[:8000]} 
                        
                        Responde de forma profesional, citando capítulos o normas si es posible.
                        Pregunta del usuario: {prompt}
                        """
                        try:
                            response = model.generate_content(prompt_sistema)
                            respuesta_texto = response.text
                            st.markdown(respuesta_texto)
                            st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_texto})
                        except Exception as e:
                            st.error(f"Hubo un error con la IA: {e}")
            st.rerun()

    with tab_slas:
        st.subheader("Tiempos de Respuesta (SLAs)")
        st.write("Según el Capítulo 12, los tiempos máximos son:")
        st.table({
            "Tipo de Caso": ["Petición general", "Queja por atención", "Consulta compleja"],
            "Tiempo Máximo": ["15 días hábiles", "15 días hábiles", "30 días hábiles"]
        })

    with tab_datos:
        st.subheader("Clasificación de Datos")
        st.info("Revisa el Capítulo 3 para ver los controles de datos sensibles (AES-256, MFA).")