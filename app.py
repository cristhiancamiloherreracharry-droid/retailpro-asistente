import streamlit as st
import google.generativeai as genai
import os
import re
import traceback

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide", page_icon="⚖️")

# --- 1. CARGA DE ESTILOS CSS ---
# --- 1. CARGA DE ESTILOS CSS ---
def cargar_css():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(directorio_actual, "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cargar_css()

# --- 2. CONFIGURACIÓN DE IA ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("⚠️ Falta configurar GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()
    
genai.configure(api_key=GOOGLE_API_KEY)

def cargar_y_parsear_marco():
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # CORRECCIÓN CLAVE: Busca cualquier cantidad de numerales (##, ###, etc.)
        partes = re.split(r'^(#+\s.+)', contenido, flags=re.MULTILINE)
        capitulos = {}
        
        if len(partes) > 1:
            for i in range(1, len(partes), 2):
                # Limpia los numerales para dejar el título puro en el acordeón
                titulo = partes[i].replace('#', '').strip()
                contenido_cap = partes[i+1].strip() if (i+1) < len(partes) else ""
                
                if titulo and contenido_cap:
                    capitulos[titulo] = contenido_cap
        else:
            capitulos["Documento Completo"] = contenido
            
        return capitulos, contenido
    except Exception as e:
        return {"Error": f"No se pudo cargar el marco legal. Detalle: {e}"}, ""

capitulos_dict, documento_completo = cargar_y_parsear_marco()

instrucciones = f"Eres el Asistente Ejecutivo de RetailPro. Marco normativo: {documento_completo}. Responde basado estrictamente en este documento."
model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=instrucciones)

# --- INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if "mensajes" not in st.session_state: 
    st.session_state.mensajes = []
if "debug_log" not in st.session_state:
    st.session_state.debug_log = "Sistema iniciado correctamente. Esperando consultas..."

# --- 3. UI PRINCIPAL ---
st.title("⚖️ Asistente de Gobernanza RetailPro")
col1, col2 = st.columns([1, 1])

# --- COLUMNA IZQUIERDA: MARCO NORMATIVO ---
with col1:
    st.markdown('<div class="custom-card"><div class="card-header-blue">📄 Marco Normativo</div></div>', unsafe_allow_html=True)
    
    with st.container(height=650, border=True):
        for titulo, contenido in capitulos_dict.items():
            # Crea un expander por cada capítulo detectado (ej. "CAPÍTULO 1. Gobierno Corporativo")
            with st.expander(titulo):
                # Renderiza todo el contenido interno (negritas, tablas, listas) tal cual tu archivo
                st.markdown(contenido)

# --- COLUMNA DERECHA: CHAT IA, SUGERENCIAS Y LOG ---
with col2:
    st.markdown('<div class="custom-card"><div class="card-header-purple">🤖 Chat Legal</div></div>', unsafe_allow_html=True)
    
    # Contenedor del Chat
    contenedor_chat = st.container(height=380, border=True)
    with contenedor_chat:
        for m in st.session_state.mensajes:
            with st.chat_message(m["rol"]): 
                st.markdown(m["contenido"])

    # Sugerencias rápidas
    st.markdown("<p style='font-size: 0.9rem; color: #64748b; margin-top: 10px; margin-bottom: 5px;'>💡 Sugerencias rápidas:</p>", unsafe_allow_html=True)
    sug1, sug2, sug3 = st.columns(3)
    
    prompt_sugerido = None
    if sug1.button("⏱️ SLAs de PQR", use_container_width=True): prompt_sugerido = "¿Cuáles son los tiempos máximos para responder PQR?"
    if sug2.button("🔐 Datos Sensibles", use_container_width=True): prompt_sugerido = "¿Qué reglas existen sobre datos sensibles?"
    if sug3.button("📝 Continuidad", use_container_width=True): prompt_sugerido = "¿Cuáles son las directrices de continuidad de negocio?"

    # Log de Depuración
    with st.expander("🛠️ Consola de Depuración (Log de API)"):
        st.code(st.session_state.debug_log, language="python")

    # Input del Chat
    prompt_usuario = st.chat_input("Consulta aquí (Ej: ¿Cuáles son las reglas de seguridad?):")
    prompt_final = prompt_sugerido or prompt_usuario
    
    if prompt_final:
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_final})
        with contenedor_chat:
            with st.chat_message("user"): 
                st.markdown(prompt_final)
            
            with st.chat_message("assistant"):
                with st.spinner("Analizando marco normativo..."):
                    try:
                        respuesta = model.generate_content(prompt_final)
                        res = respuesta.text
                        st.markdown(res)
                        
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": res})
                        st.session_state.debug_log = f"✅ ÉXITO:\nPrompt: '{prompt_final}'\nRespuesta generada correctamente."
                        
                    except Exception as e:
                        error_trace = traceback.format_exc()
                        st.session_state.debug_log = f"❌ ERROR DE API:\n{error_trace}"
                        
                        error_msg = "⚠️ Hubo un fallo de conexión con la IA. Revisa la Consola de Depuración para ver el detalle técnico."
                        st.error(error_msg)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": error_msg})
        
        st.rerun()
