import streamlit as st
import google.generativeai as genai
import os
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide", page_icon="⚖️")

# --- 1. CARGA DE ESTILOS CSS ---
def cargar_css():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(directorio_actual, "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No se encontró el archivo estilos.css")

cargar_css()

# --- 2. CONFIGURACIÓN DE IA ---
# ⚠️ PON AQUÍ TU API KEY VÁLIDA
GOOGLE_API_KEY = "AIzaSyBtPFRmk0FMwLrPIfsrkEEm5r3pCxOeKNc"
genai.configure(api_key=GOOGLE_API_KEY)

def cargar_y_parsear_marco():
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Divide por "# " o "CAPÍTULO"
        partes = re.split(r'^(#\s.+|CAPÍTULO\s.+)', contenido, flags=re.MULTILINE)
        capitulos = {}
        
        if len(partes) > 1:
            for i in range(1, len(partes), 2):
                titulo = partes[i].replace('# ', '').strip()
                contenido_cap = partes[i+1].strip() if (i+1) < len(partes) else ""
                if titulo and contenido_cap:
                    capitulos[titulo] = contenido_cap
        else:
            capitulos["Documento Completo"] = contenido
            
        return capitulos, contenido
    except Exception as e:
        return {"Error": f"No se pudo cargar el marco legal. Detalle: {e}"}, ""

capitulos_dict, documento_completo = cargar_y_parsear_marco()

# --- LÓGICA IA ---
instrucciones = f"Eres el Asistente Ejecutivo de RetailPro. Marco normativo: {documento_completo}. Responde basado estrictamente en este documento."
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instrucciones)

# --- 3. UI PRINCIPAL ---
st.title("⚖️ Asistente de Gobernanza RetailPro")
col1, col2 = st.columns([1, 1])

# --- COLUMNA IZQUIERDA: MARCO NORMATIVO ---
with col1:
    st.markdown('<div class="custom-card"><div class="card-header-blue">📄 Marco Normativo</div></div>', unsafe_allow_html=True)
    
    with st.container(height=600, border=True):
        for titulo, contenido in capitulos_dict.items():
            with st.expander(titulo):
                st.markdown(contenido)

# --- COLUMNA DERECHA: CHAT IA Y SUGERENCIAS ---
with col2:
    st.markdown('<div class="custom-card"><div class="card-header-purple">🤖 Chat Legal</div></div>', unsafe_allow_html=True)
    
    contenedor_chat = st.container(height=420, border=True)
    
    if "mensajes" not in st.session_state: 
        st.session_state.mensajes = []
        
    with contenedor_chat:
        for m in st.session_state.mensajes:
            with st.chat_message(m["rol"]): 
                st.markdown(m["contenido"])

    # --- SECCIÓN DE SUGERENCIAS ---
    st.markdown("<p style='font-size: 0.9rem; color: #64748b; margin-bottom: 5px; margin-top: 10px;'>💡 Sugerencias rápidas:</p>", unsafe_allow_html=True)
    sug1, sug2, sug3 = st.columns(3)
    
    prompt_sugerido = None
    if sug1.button("⏱️ SLAs de PQR"): prompt_sugerido = "¿Cuáles son los tiempos máximos para responder PQR?"
    if sug2.button("🔐 Datos Sensibles"): prompt_sugerido = "¿Qué reglas existen sobre datos sensibles?"
    if sug3.button("📝 Continuidad"): prompt_sugerido = "¿Cuáles son las directrices de continuidad de negocio?"

    # --- GESTIÓN DEL INPUT (Manual o por botón) ---
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
                    except Exception as e:
                        error_msg = f"**Error de la API:** Revisa tu API Key. Detalle técnico: {e}"
                        st.error(error_msg)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": error_msg})
