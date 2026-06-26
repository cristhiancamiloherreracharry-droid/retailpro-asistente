import streamlit as st
import google.generativeai as genai
import re
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide", page_icon="⚖️")

# --- CARGA DE ESTILOS CSS ---
def cargar_css():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(directorio_actual, "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cargar_css()

# --- CONFIGURACIÓN DE IA ---
GOOGLE_API_KEY = "AIzaSyB1H--nWeVqnTninyrYSRrftA5bI2gnGr8"
genai.configure(api_key=GOOGLE_API_KEY)

def cargar_y_parsear_marco():
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Divide por títulos que empiezan con #
        partes = re.split(r'(^# .+)', contenido, flags=re.MULTILINE)
        capitulos = {}
        for i in range(1, len(partes), 2):
            titulo = partes[i].replace('# ', '').strip()
            contenido_cap = partes[i+1].strip()
            capitulos[titulo] = contenido_cap
        return capitulos
    except:
        return {"Error": "No se pudo cargar el marco legal. Verifica que el archivo exista."}

capitulos_dict = cargar_y_parsear_marco()
documento_completo = "\n".join([f"{t}\n{c}" for t, c in capitulos_dict.items()])

# --- LÓGICA IA ---
instrucciones = f"Eres el Asistente Ejecutivo de RetailPro. Marco normativo: {documento_completo}. Responde basado estrictamente en este documento."
# Se ajustó al modelo 1.5-flash que es la versión estable actual de la API
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instrucciones)

# --- UI PRINCIPAL ---
st.title("⚖️ Asistente de Gobernanza RetailPro")

# Definición de columnas
col1, col2 = st.columns([1, 1])

# --- COLUMNA IZQUIERDA: MARCO NORMATIVO ---
with col1:
    # Cabecera CSS personalizada azul
    st.markdown('<div class="custom-card"><div class="card-header-blue">📄 Marco Normativo</div></div>', unsafe_allow_html=True)
    
    # Contenedor con scroll para los expanders
    with st.container(height=600, border=True):
        for titulo, contenido in capitulos_dict.items():
            with st.expander(titulo):
                st.markdown(contenido)

# --- COLUMNA DERECHA: CHAT IA ---
with col2:
    # Cabecera CSS personalizada morada
    st.markdown('<div class="custom-card"><div class="card-header-purple">🤖 Chat Legal</div></div>', unsafe_allow_html=True)
    
    # Contenedor del chat
    contenedor_chat = st.container(height=480, border=True)
    
    if "mensajes" not in st.session_state: 
        st.session_state.mensajes = []
        
    with contenedor_chat:
        for m in st.session_state.mensajes:
            with st.chat_message(m["rol"]): 
                st.markdown(m["contenido"])
    
    # Input de usuario y ejecución de IA
    if prompt := st.chat_input("Consulta aquí:"):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        
        with contenedor_chat:
            with st.chat_message("user"): 
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Consultando marco legal..."):
                    try:
                        res = model.generate_content(prompt).text
                        st.markdown(res)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": res})
                    except Exception as e:
                        st.error("Error al consultar la IA. Verifica que tu API Key sea válida.")
        
        st.rerun()
