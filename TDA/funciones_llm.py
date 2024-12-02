"""
Módulo que contiene las funciones para procesar la consulta del usuario,
interactuar con el modelo LLM y calcular la ruta utilizando el algoritmo de Dijkstra.

Autor: [Samuel Partida Cabañas]
Fecha: [01/12/24]
"""

import os
import json
import heapq
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

def configurar_cliente():
    """
    Configura el cliente de Anthropic para interactuar con el modelo LLM.

    Returns:
        Anthropic: Instancia del cliente Anthropic.

    Raises:
        ValueError: Si no se encuentra la clave API en las variables de entorno.
    """
    # Obtiene la clave API desde las variables de entorno
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("No se encontró la clave API. Configura 'ANTHROPIC_API_KEY' como variable de entorno.")

    return Anthropic(api_key=api_key)

def construir_prompt_consulta(usuario_input, nodos):
    """
    Construye el prompt para enviar al modelo LLM.

    Args:
        usuario_input (str): Consulta ingresada por el usuario.
        nodos (list): Lista de nodos disponibles.

    Returns:
        str: Prompt construido para el modelo LLM.
    """
    nodos_nombres = [nodo["nombre"] for nodo in nodos]
    nodos_texto = ", ".join(nodos_nombres)
    prompt = (
        f"{HUMAN_PROMPT} Eres un asistente de navegación amable para una universidad. "
        f"Puedes guiar al usuario desde un lugar de origen a su destino basándote en esta lista de ubicaciones: {nodos_texto}. "
        f"Por favor, proporciona instrucciones detalladas sobre cómo llegar, como en este ejemplo:\n\n"
        f"Ejemplo: 'Primero, sal de Coordinación de deportes hacia Canchas fútbol voleibol pista. Luego, dirígete hacia Artes. Por último, continúa hasta INIAT.'\n\n"
        f"Consulta del usuario: {usuario_input}\n\n{AI_PROMPT}"
    )
    return prompt

def ejecutar_llm(prompt, modelo="claude-2", max_tokens=300):
    """
    Ejecuta el modelo LLM con el prompt proporcionado.

    Args:
        prompt (str): Prompt a enviar al modelo LLM.
        modelo (str, optional): Nombre del modelo a utilizar. Por defecto 'claude-2'.
        max_tokens (int, optional): Máximo número de tokens a generar. Por defecto 300.

    Returns:
        str: Respuesta generada por el modelo LLM.
    """
    cliente = configurar_cliente()
    respuesta = cliente.completions.create(
        model=modelo,
        prompt=prompt,
        max_tokens_to_sample=max_tokens
    )
    return respuesta.completion.strip()

def cargar_grafo(nodos, topologia):
    """
    Carga el grafo desde los nodos y la topología.

    Args:
        nodos (list): Lista de nodos disponibles.
        topologia (list): Lista de conexiones entre nodos con sus pesos.

    Returns:
        dict: Representación del grafo como un diccionario.
    """
    grafo = {nodo["id"]: {} for nodo in nodos}
    for conexion in topologia:
        origen, destino, peso = conexion.strip().split(":")
        peso = float(peso)
        grafo[origen][destino] = peso
        grafo[destino][origen] = peso  # Si el grafo es no dirigido
    return grafo

def dijkstra(grafo, inicio, fin):
    """
    Implementación del algoritmo de Dijkstra para encontrar la ruta más corta.

    Args:
        grafo (dict): Representación del grafo.
        inicio (str): Nodo de inicio.
        fin (str): Nodo de destino.

    Returns:
        list: Lista de IDs de nodos que representan el camino más corto.
    """
    cola = [(0, inicio, [])]
    visitados = set()
    while cola:
        (costo, actual, camino) = heapq.heappop(cola)
        if actual in visitados:
            continue
        visitados.add(actual)
        camino = camino + [actual]
        if actual == fin:
            return camino
        for vecino, peso in grafo[actual].items():
            if vecino not in visitados:
                heapq.heappush(cola, (costo + peso, vecino, camino))
    return None

def obtener_id_nodo(nombre, nodos):
    """
    Obtiene el ID de un nodo a partir de su nombre.

    Args:
        nombre (str): Nombre del nodo.
        nodos (list): Lista de nodos disponibles.

    Returns:
        str or None: ID del nodo si se encuentra, None en caso contrario.
    """
    for nodo in nodos:
        if nodo["nombre"].lower() == nombre.lower():
            return nodo["id"]
    return None

def extraer_origen_destino(consulta, nodos):
    """
    Extrae el origen y destino de la consulta del usuario.

    Args:
        consulta (str): Consulta ingresada por el usuario.
        nodos (list): Lista de nodos disponibles.

    Returns:
        tuple: (origen, destino) si se encuentran, (None, None) en caso contrario.
    """
    import re
    # Expresión regular para extraer "de [origen] a [destino]"
    patron = r"de (.+?) a (.+)"
    match = re.search(patron, consulta.lower())
    if match:
        origen = match.group(1).strip()
        destino = match.group(2).strip()
        # Validar que los nombres existan en nodos
        origen_valido = any(nodo["nombre"].lower() == origen.lower() for nodo in nodos)
        destino_valido = any(nodo["nombre"].lower() == destino.lower() for nodo in nodos)
        if origen_valido and destino_valido:
            return origen, destino
    return None, None

def generar_descripcion_ruta(ruta_nombres):
    """
    Genera una descripción detallada de la ruta para el usuario.

    Args:
        ruta_nombres (list): Lista de nombres de los nodos en la ruta.

    Returns:
        str: Descripción detallada de la ruta.
    """
    descripcion = "Para llegar a tu destino, sigue estos pasos:\n"
    for i in range(len(ruta_nombres) - 1):
        descripcion += f"- Desde {ruta_nombres[i]}, dirígete hacia {ruta_nombres[i + 1]}.\n"
    descripcion += "¡Has llegado a tu destino!"
    return descripcion

def procesar_consulta(usuario_input, nodos):
    """
    Procesa la consulta del usuario y genera una respuesta detallada.

    Args:
        usuario_input (str): Consulta ingresada por el usuario.
        nodos (list): Lista de nodos disponibles.

    Returns:
        str: Respuesta generada para el usuario.
    """
    try:
        # Intentar extraer origen y destino de la consulta del usuario
        origen, destino = extraer_origen_destino(usuario_input, nodos)

        if origen and destino:
            # Cargar el grafo
            with open("topologia.txt", "r") as file:
                topologia = file.readlines()
            grafo = cargar_grafo(nodos, topologia)

            id_origen = obtener_id_nodo(origen, nodos)
            id_destino = obtener_id_nodo(destino, nodos)

            if id_origen and id_destino:
                ruta_ids = dijkstra(grafo, id_origen, id_destino)
                if ruta_ids:
                    ruta_nombres = []
                    for id_nodo in ruta_ids:
                        for nodo in nodos:
                            if nodo["id"] == id_nodo:
                                ruta_nombres.append(nodo["nombre"])
                                break
                    descripcion_ruta = generar_descripcion_ruta(ruta_nombres)
                    return descripcion_ruta
                else:
                    return "No se encontró una ruta entre los lugares especificados."
            else:
                return "No pude identificar correctamente los lugares en tu consulta."
        else:
            # Si no se pudo extraer origen y destino, usar el LLM para generar una respuesta
            prompt = construir_prompt_consulta(usuario_input, nodos)
            respuesta_llm = ejecutar_llm(prompt)
            if respuesta_llm:
                return respuesta_llm
            else:
                return "Lo siento, no pude entender tu solicitud."
    except Exception as e:
        return f"Error procesando la consulta: {str(e)}"
