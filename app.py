import streamlit as st
import os
import google.generativeai as genai

st.set_page_config(page_title="RetailPro - Asistente Legal", layout="wide")

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

# Header Superior (Logo y Nombre)
st.markdown("""
    <div class="main-header">
        <img src="https://cdn-icons-png.flaticon.com/512/584/584611.png" width="40" style="margin-right:15px">
        <div style="font-size: 24px; font-weight: 700; color: #1E293B;">RetailPro <span style="font-weight:400; font-size:16px; color:#64748B;">| Asistente Legal Interactivo</span></div>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="card-header-blue">📘 Marco Normativo</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Contenido del marco legal
        st.markdown("### Marco legal y de referencia")
        st.info("RetailPro adoptará como referencias mínimas la legislación comercial, laboral, tributaria...")
        
        st.markdown("### Definiciones")
        with st.expander("🏛️ Gobierno corporativo"):
            st.write("Sistema mediante el cual RetailPro es dirigida y controlada.")
        with st.expander("⚠️ Riesgo"):
            st.write("Evento incierto que puede afectar objetivos.")
        with st.expander("🛡️ Control"):
            st.write("Medida preventiva, detectiva o correctiva.")

with col2:
    st.markdown('<div class="card-header-purple">💬 Chat Legal Interactivo</div>', unsafe_allow_html=True)
    
    # Tabs como en la imagen 2
    tab_chat, tab_slas, tab_datos = st.tabs(["💬 Chat", "📋 SLAs de PDF", "🗄️ Datos Sensibles"])
    
    with tab_chat:
        # Espacio del chat
        contenedor_chat = st.container(height=450)
        
        if "mensajes" not in st.session_state:
            st.session_state.mensajes = [{"rol": "assistant", "contenido": "¡Hola! Soy tu asistente legal de RetailPro. ¿En qué puedo ayudarte hoy?"}]

        with contenedor_chat:
            for m in st.session_state.mensajes:
                with st.chat_message(m["rol"]):
                    st.markdown(m["contenido"])

        if prompt := st.chat_input("Escribe tu pregunta sobre RetailPro..."):
            st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
            st.rerun()