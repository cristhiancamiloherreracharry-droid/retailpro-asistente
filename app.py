import streamlit as st
import google.generativeai as genai
import os
import re

# --- CONFIGURACIÓN E IA ---
# ... (Tu código de configuración y modelo igual que antes) ...

def cargar_y_parsear_marco():
    try:
        with open("marco_legal.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Regex para separar el texto por títulos de capítulo (asumimos títulos con #)
        # Esto busca patrones como "# Titulo"
        partes = re.split(r'(^# .+)', contenido, flags=re.MULTILINE)
        
        capitulos = {}
        for i in range(1, len(partes), 2):
            titulo = partes[i].replace('# ', '').strip()
            contenido_cap = partes[i+1].strip()
            capitulos[titulo] = contenido_cap
            
        return capitulos
    except:
        return {"Error": "No se pudo cargar el marco."}

capitulos_dict = cargar_y_parsear_marco()

# --- INTERFAZ ---
with col1:
    st.subheader("📄 Marco Normativo")
    with st.container(height=600, border=True):
        # Generar expanders dinámicamente basados en el archivo
        for titulo, contenido in capitulos_dict.items():
            with st.expander(titulo):
                st.markdown(contenido)