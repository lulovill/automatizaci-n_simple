import re
import sys
# Importamos las funciones de lógica de negocio desde nuestro paquete de funciones
from funciones_agente.obtener_precio_accion import obtener_precio_accion
from funciones_agente.obtener_clima import obtener_clima
# Importamos utilidades para limpiar el texto del usuario
from utils.sanitizar import sanitizar

def procesar_input(texto):

    if "clima" in texto or "temperatura" in texto or "tiempo" in texto:
        return "clima"

    if "precio" in texto or "accion" in texto:
        return "precio"

    return None

def chatbot():
    """
    Función principal que inicia el chatbot interactivo por consola.
    Maneja el ciclo de vida del chat, recibe el input del usuario y 
    determina qué acción realizar basándose en expresiones regulares.
    """
    print("*** Chatbot v1.0.0***")
    print("Hola, soy el Chatbot v1.0.0. Puedo ayudarte a obtener precios de acciones o indicarte")
    print("la temperatura actual en cualquier ciudad del mundo.")
    print("Me puedes hacer preguntas, por ejemplo ¿cuál es el precio de una acción de Microsoft?")
    print("¿cuál es la temperatura actual en la Ciudad de México?\n")

    # Ciclo infinito para mantener el chat activo hasta que el usuario decida salir
    while True:
        try:
            user_input = sanitizar(input("--> "))

            if not user_input:
                continue
                        
            # Comprobar si el usuario desea finalizar la conversación
            if user_input.lower() in ["salir", "exit", "quit", "adiós", "adios"]:
                print(">>> ¡Hasta luego!")
                break

            intencion = procesar_input(user_input)
                # Caso 1: El usuario pregunta por acciones
            if intencion == "precio":
                # El agente espera (driver, user_input). Pasamos None como driver en esta versión simple.
                precio = obtener_precio_accion(user_input)
                if precio:
                    print(f">>> {precio}")
                else:
                    print(">>> Lo siento, no pude encontrar el precio de la acción.")
    
            # Caso 2: El usuario pregunta por el clima
            elif intencion == "clima":
                # El agente espera (driver, user_input)
                clima = obtener_clima(user_input)
                if clima:
                    print(f">>> {clima}")
                else:
                    print(">>> Lo siento, no pude obtener el clima.")
            
            # Caso 3: No se detecta ninguna intención conocida
            else:
                print(">>> No estoy seguro de cómo ayudarte con eso. Prueba preguntando por el precio de una acción o el clima en una ciudad.")

        except KeyboardInterrupt:
            # Capturar Ctrl+C para salir elegantemente
            print("\n>>> ¡Hasta luego!")
            break
        except Exception as e:
            # Capturar cualquier otro error inesperado para evitar que el programa se cierre
            print(f">>> Ocurrió un error: {e}")

# Punto de entrada principal del script
if __name__ == "__main__":
    chatbot()