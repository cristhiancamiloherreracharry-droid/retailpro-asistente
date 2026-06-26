import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente Ejecutivo RetailPro", layout="wide")

# Tu API KEY configurada
GOOGLE_API_KEY = "AQ.Ab8RN6IPy6WKUTcFmut8rJye-hjL-IJHuxl-y0dbvaitjwW4wQ"
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
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instrucciones)

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
    if "mensajes" not in st.session_state: st.session_state.mensajes = []
    for m in st.session_state.mensajes:
        with st.chat_message(m["rol"]): st.markdown(m["contenido"])
    
    if prompt := st.chat_input("Consulta aquí:"):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(prompt).text
                st.markdown(res)
                st.session_state.mensajes.append({"rol": "assistant", "contenido": res})
            except Exception as e:
                st.error("Error al consultar la IA. Verifica que tu API Key sea válida.")
