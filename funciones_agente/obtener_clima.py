
import re
import requests


def obtener_clima(user_input):
    """
    Recibe la pregunta completa, identifica la ciudad,
    consulta Open-Meteo y devuelve las condiciones actuales.
    """

    # 1. Preparar la pregunta
    pregunta = user_input.lower().strip()
    pregunta = re.sub(r"[¿?¡!,;:]", " ", pregunta)
    pregunta = re.sub(r"\s+", " ", pregunta).strip()

    # 2. Extraer el nombre de la ciudad
    pregunta = re.sub(
        r"^(?:dime|busca|consulta|quiero saber)\s+",
        "",
        pregunta
    )

    pregunta = re.sub(
        r"^(?:cual es|como esta|como se encuentra)\s+",
        "",
        pregunta
    )

    pregunta = re.sub(
        r"^(?:el\s+)?(?:clima|tiempo|temperatura)\s+",
        "",
        pregunta
    )

    pregunta = re.sub(
        r"^(?:actual|actualmente)\s+",
        "",
        pregunta
    )

    pregunta = re.sub(
        r"^(?:de|en)\s+",
        "",
        pregunta
    )

    pregunta = re.sub(
        r"\s+(?:hoy|ahora|actualmente|por favor)$",
        "",
        pregunta
    )

    ciudad = pregunta.strip()

    if not ciudad:
        return "No pude identificar la ciudad."

    # 3. Configurar la conexión
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        # 4. Buscar la ciudad mediante Geocoding
        geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        params = {
            "name": ciudad,
            "count": 10,
            "language": "es",
            "format": "json"
        }

        response = requests.get(
            geocoding_url,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        resultados = response.json().get("results", [])

        if not resultados:
            return f"No encontré la ciudad: {ciudad}"

        # 5. Seleccionar la coincidencia
        seleccion = next(
            (
                lugar for lugar in resultados
                if lugar.get("name", "").lower() == ciudad
            ),
            resultados[0]
        )

        latitud = seleccion["latitude"]
        longitud = seleccion["longitude"]

        nombre_ciudad = seleccion["name"]
        pais = seleccion.get("country", "")

        # 6. Consultar el clima mediante Forecast API
        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        weather_params = {
            "latitude": latitud,
            "longitude": longitud,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            headers=headers,
            timeout=15
        )

        weather_response.raise_for_status()

        datos = weather_response.json()
        actual = datos["current"]
        unidades = datos["current_units"]

        # 7. Traducir el código meteorológico
        codigos_clima = {
            0: "Despejado",
            1: "Principalmente despejado",
            2: "Parcialmente nublado",
            3: "Cubierto",
            45: "Niebla",
            48: "Niebla con escarcha",
            51: "Llovizna ligera",
            53: "Llovizna moderada",
            55: "Llovizna intensa",
            61: "Lluvia ligera",
            63: "Lluvia moderada",
            65: "Lluvia intensa",
            71: "Nieve ligera",
            73: "Nieve moderada",
            75: "Nieve intensa",
            80: "Chubascos ligeros",
            81: "Chubascos moderados",
            82: "Chubascos intensos",
            95: "Tormenta eléctrica",
            96: "Tormenta con granizo ligero",
            99: "Tormenta con granizo intenso"
        }

        codigo = actual["weather_code"]
        condicion = codigos_clima.get(
            codigo,
            "Condición meteorológica no identificada"
        )

        # 8. Obtener los datos
        temperatura = actual["temperature_2m"]
        sensacion = actual["apparent_temperature"]
        humedad = actual["relative_humidity_2m"]
        viento = actual["wind_speed_10m"]

        unidad_temp = unidades["temperature_2m"]
        unidad_viento = unidades["wind_speed_10m"]

        # 9. Devolver el resultado
        return (
            f"Clima en {nombre_ciudad}, {pais}\n"
            f"Condición: {condicion}\n"
            f"Temperatura: {temperatura}{unidad_temp}\n"
            f"Sensación térmica: {sensacion}{unidad_temp}\n"
            f"Humedad: {humedad}%\n"
            f"Viento: {viento} {unidad_viento}"
        )

    except requests.RequestException as e:
        return f"Error de conexión con Open-Meteo: {e}"

    except (ValueError, KeyError, TypeError) as e:
        return f"Error al procesar los datos: {e}"
