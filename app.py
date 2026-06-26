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
    st.subheader("🤖 Chat Legal interactivo")
    
    # 1. Contenedor fijo con scroll (El secreto de la UI limpia)
    contenedor_chat = st.container(height=480, border=True)
    
    if "mensajes" not in st.session_state: 
        st.session_state.mensajes = []
        
    # Dibujar el historial DENTRO del contenedor
    with contenedor_chat:
        for m in st.session_state.mensajes:
            with st.chat_message(m["rol"]): 
                st.markdown(m["contenido"])
    
    # 2. Sugerencias rápidas (Botones tipo Chips)
    st.caption("💡 Sugerencias de consulta rápida:")
    c1, c2, c3 = st.columns(3)
    prompt_sugerido = None
    
    if c1.button("⏱️ SLAs de PQR"): 
        prompt_sugerido = "¿Cuáles son los tiempos máximos internos de respuesta para las PQR?"
    if c2.button("🔐 Datos Sensibles"): 
        prompt_sugerido = "¿Cuáles son las normas y controles mínimos para los datos sensibles?"
    if c3.button("📝 Continuidad"): 
        prompt_sugerido = "¿Qué reglas existen para la continuidad del negocio y DRP?"
    
    # 3. Input tradicional de chat
    prompt_usuario = st.chat_input("Escribe tu pregunta sobre RetailPro...")
    
    # Evaluar si el usuario escribió a mano o presionó un botón
    prompt_final = prompt_sugerido or prompt_usuario
    
    if prompt_final:
        # Guardar en memoria
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_final})
        
        # Procesar visualmente DENTRO del contenedor con scroll
        with contenedor_chat:
            with st.chat_message("user"): 
                st.markdown(prompt_final)
            
            with st.chat_message("assistant"):
                with st.spinner("Analizando el marco normativo..."):
                    try:
                        respuesta = model.generate_content(prompt_final)
                        texto = respuesta.text
                        st.markdown(texto)
                        st.session_state.mensajes.append({"rol": "assistant", "contenido": texto})
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
        
        # Este comando reinicia la UI sutilmente para empujar el scroll hacia abajo
        st.rerun()
