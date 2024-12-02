"""
Archivo principal de la aplicación Streamlit para la Guía Interactiva de la Universidad.

Este script configura la interfaz de usuario, maneja la interacción con el usuario
y muestra imágenes y mapas para mejorar la experiencia del usuario.

Autor: [Samuel Partida Cabañas]
Fecha: [01/12/24]
"""

import os
import json
import streamlit as st
from funciones_llm import procesar_consulta

def cargar_nodos():
    """
    Carga los nodos desde el archivo JSON.

    Returns:
        list: Lista de nodos cargados desde 'nodos.json'.
    """
    ruta_nodos = os.path.join(os.path.dirname(__file__), "nodos.json")
    with open(ruta_nodos, "r", encoding="utf-8") as file:
        return json.load(file)["nodos"]

def main():
    """
    Función principal que ejecuta la aplicación Streamlit.
    Configura la interfaz, carga los nodos y procesa las consultas del usuario.
    """
    # Configuración de la página
    st.set_page_config(page_title="Guía Interactiva de la Universidad", page_icon="🗺️")

    # Título centrado
    st.markdown(
        """
        <h1 style='text-align: center;'>🗺️ Guía Interactiva de la Universidad</h1>
        """,
        unsafe_allow_html=True
    )

    # Centrar el logo de la universidad usando columnas
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.write("")  # Espacio vacío a la izquierda
    with col2:
        ruta_logo = os.path.join(os.path.dirname(__file__), "logo_universidad.png")
        st.image(ruta_logo, use_container_width=True)  # Logo centrado
    with col3:
        st.write("")  # Espacio vacío a la derecha

    # Mostrar imagen del mapa de la universidad
    ruta_mapa = os.path.join(os.path.dirname(__file__), "mapa_universidad.png")
    st.image(ruta_mapa, use_container_width=True)

    # Separador
    st.markdown("---")

    # Cargar nodos
    nodos = cargar_nodos()

    # Entrada del usuario
    st.header("Consulta de rutas")
    usuario_input = st.text_input(
        "Ingresa tu consulta:",
        placeholder="Por ejemplo: Quiero ir de Coordinación de deportes a Artes."
    )

    if st.button("Enviar"):
        if usuario_input:
            respuesta = procesar_consulta(usuario_input, nodos)
            st.success(respuesta)
        else:
            st.warning("Por favor, ingresa una consulta.")

if __name__ == "__main__":
    main()
