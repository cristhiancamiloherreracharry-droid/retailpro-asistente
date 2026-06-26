import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide")

# Tu API KEY configurada
GOOGLE_API_KEY = "AIzaSyB1H--nWeVqnTninyrYSRrftA5bI2gnGr8"
genai.configure(api_key=GOOGLE_API_KEY)

# --- CARGA DE DOCUMENTO ---
def cargar_marco():
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Error al cargar el marco legal."

documento = cargar_marco()

# --- LÓGICA IA ---
instrucciones = f"Eres el Asistente Ejecutivo de RetailPro. Marco normativo: {documento}. Reglas: Responde solo basado en este documento."
model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=instrucciones)

# --- UI ---
st.title("⚖️ Asistente de Gobernanza RetailPro")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 Marco Normativo")
    # El contenedor mantiene el tamaño fijo de 600px con scroll
    with st.container(height=600, border=True):
        # st.markdown es el motor que renderiza las negritas, tablas y títulos
        st.markdown(documento)

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
