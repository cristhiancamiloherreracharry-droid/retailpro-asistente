import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente de Gobernanza RetailPro", layout="wide")

# --- 2. CONFIGURACIÓN DE LA API DE GOOGLE ---
# Reemplaza 'TU_API_KEY' con tu clave real de Google AI Studio
GOOGLE_API_KEY = "TU_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

# --- 3. BASE DE CONOCIMIENTO (SYSTEM PROMPT) ---
# Aquí inyectamos el documento oficial para que el LLM lo use como contexto estricto
documento_base = """
MARCO NORMATIVO INTEGRAL RetailPro.
Capítulo 1. Gobierno Corporativo: La Junta Directiva aprueba estrategia; Gerencia ejecuta. Todo gasto requiere aprobación proporcional al riesgo.
Capítulo 3. Gobierno de Datos: Datos sensibles (personales, nómina) exigen AES-256, MFA obligatorio y no se pueden copiar a dispositivos personales.
Capítulo 4. Seguridad de la Información: MFA obligatorio para VPN y sistemas financieros. Contraseñas de 12 caracteres. Prohibido compartir cuentas.
Capítulo 10. Contratación: Contratos de Prestación de Servicios enfocados en entregables (hitos), independencia total, sin subordinación laboral.
Capítulo 12. Gestión de PQR: 
- Petición general: 15 días hábiles.
- Reclamo por producto/servicio: 15 días hábiles.
- Caso crítico (fraude, seguridad): Escalamiento inmediato en máximo 2 horas hábiles a Gerencia.
Toda PQR debe gestionarse mediante formatos estandarizados (F-PQR-01 a F-PQR-12).
"""

instrucciones_sistema = f"""
Actúa como el Asistente Ejecutivo de Gobernanza y Consultoría Legal de 'RetailPro'. 
Tu única base de conocimiento es el siguiente documento oficial: {documento_base}
Reglas:
1. Responde siempre basándote EXCLUSIVAMENTE en el documento proporcionado.
2. Si te preguntan algo que no está en el texto, responde: "Debo elevar esta consulta al Comité de Gobierno correspondiente, ya que no se encuentra en mis directrices actuales."
3. Usa un tono ejecutivo, técnico y formal.
"""

# Inicializar el modelo con las instrucciones del sistema
modelo = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=instrucciones_sistema
)

# Inicializar el historial de chat en la sesión
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- 4. DISEÑO DE LA INTERFAZ (UI/UX) ---
st.title("⚖️ Portal de Gobernanza y Seguridad - RetailPro")
st.markdown("---")

# Dividir la pantalla en 2 columnas (50% y 50%)
col1, col2 = st.columns([1, 1])

# COLUMNA IZQUIERDA: VISUALIZADOR DEL DOCUMENTO
with col1:
    st.subheader("📄 Marco Normativo Integral")
    st.info("Explora el documento oficial o consulta al asistente en el panel derecho.")
    
    # Contenedor con scroll para el documento largo
    with st.container(height=500):
        st.markdown("""
        ### CAPÍTULO 1. Gobierno Corporativo
        **Objetivo:** Establecer las reglas de dirección, control y toma de decisiones de RetailPro.
        - **Junta Directiva:** Aprobar estrategia, presupuesto y apetito de riesgo.
        - **Gerencia General:** Ejecutar estrategia y representar legalmente.
        
        ### CAPÍTULO 3. Gobierno de Datos
        - **Datos Sensibles:** Tarjetas, nómina, biometría. Controles: MFA obligatorio, AES-256.
        - **Norma GD-04:** Se prohíbe copiar datos sensibles a dispositivos personales.
        
        ### CAPÍTULO 10. Contratación
        - **Prestación de Servicios:** Enfoque en entregables, SLA, penalidades y confidencialidad. No existe subordinación.
        
        ### CAPÍTULO 12. Gestión de PQR
        - **Casos críticos:** Escalamiento en máximo dos horas hábiles.
        - **Peticiones generales:** 15 días hábiles para respuesta.
        *(Desplázate para leer más...)*
        """)

# COLUMNA DERECHA: CHATBOT DE IA
with col2:
    st.subheader("🤖 Asistente Virtual Legal")
    
    # Mostrar el historial de mensajes
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])
            
    # Capturar la entrada del usuario
    pregunta = st.chat_input("Ej: ¿Cuál es el SLA para escalar un caso crítico de PQR?")
    
    if pregunta:
        # Mostrar la pregunta del usuario
        with st.chat_message("user"):
            st.markdown(pregunta)
        st.session_state.mensajes.append({"rol": "user", "contenido": pregunta})
        
        # Generar la respuesta de Gemini
        with st.chat_message("assistant"):
            respuesta_placeholder = st.empty()
            # Enviar el historial de mensajes al modelo para mantener contexto
            chat = modelo.start_chat(history=[
                {"role": m["rol"] if m["rol"] == "user" else "model", "parts": [m["contenido"]]} 
                for m in st.session_state.mensajes[:-1]
            ])
            
            respuesta_generada = chat.send_message(pregunta)
            texto_respuesta = respuesta_generada.text
            
            respuesta_placeholder.markdown(texto_respuesta)
            
        # Guardar la respuesta en el historial
        st.session_state.mensajes.append({"rol": "assistant", "contenido": texto_respuesta})
