

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def obtener_precio_accion(user_input):
    """
    Recibe la pregunta completa, identifica la empresa o ticker,
    consulta Yahoo Finance y devuelve el precio encontrado.
    """

    # 1. Preparar la pregunta
    pregunta = user_input.lower().strip()

    pregunta = re.sub(r"[¿?¡!,;:]", " ", pregunta)
    pregunta = re.sub(r"\s+", " ", pregunta).strip()

    # 2. Extraer el nombre de la empresa o ticker
    patron = (
    r"^(?:(?:cual es|dime|busca|consulta|quiero saber)\s+)?"
    r"(?:el\s+)?"
    r"(?:(?:precio|cotizacion|valor)\s+)?"
    r"(?:(?:de\s+)?(?:la\s+)?acciones?\s+(?:de\s+)?)?"
    r"(?:de\s+)?"
)

    company_name = re.sub(patron, "", pregunta).strip()

    # Eliminar expresiones finales que no pertenecen al nombre
    company_name = re.sub(
        r"\s+(?:hoy|ahora|actualmente|por favor)$",
        "",
        company_name
    ).strip()

    if not company_name:
        return "No pude identificar la empresa o ticker."

    # 3. Configurar la conexión con Yahoo Finance
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
        )
    }

    try:
        # 4. Buscar la empresa para obtener su ticker
        search_url = (
            "https://query1.finance.yahoo.com/v1/finance/search"
        )

        params = {
            "q": company_name,
            "quotesCount": 10,
            "newsCount": 0
        }

        response = requests.get(
            search_url,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        resultados = response.json().get("quotes", [])

        acciones = [
            resultado for resultado in resultados
            if resultado.get("quoteType") == "EQUITY"
        ]

        if not acciones:
            return f"No encontré una acción para: {company_name}"

        # Priorizar coincidencia exacta si el usuario escribió un ticker
        ticker = company_name.upper()

        seleccion = next(
            (
                accion for accion in acciones
                if accion.get("symbol", "").upper() == ticker
            ),
            acciones[0]
        )

        ticker = seleccion["symbol"]

        # 5. Consultar la página de cotización
        quote_url = (
            f"https://finance.yahoo.com/quote/{quote(ticker, safe='')}/"
        )

        quote_response = requests.get(
            quote_url,
            headers=headers,
            timeout=15
        )

        quote_response.raise_for_status()

        # 6. Analizar el HTML
        soup = BeautifulSoup(
            quote_response.text,
            "html.parser"
        )

        # Selector comprobado en nuestra prueba de terminal
        price_element = soup.select_one(
            '[data-testid="qsp-price"]'
        )

        if price_element is None:
            return (
                f"Encontré {ticker}, pero no pude localizar "
                "el precio en el HTML."
            )

        price = price_element.get_text(strip=True)

        if not price:
            return f"No pude obtener el precio de {ticker}."

        # 7. Devolver el resultado al main.py
        nombre_empresa = (
            seleccion.get("shortname")
            or seleccion.get("longname")
            or ticker
        )

        return f"{nombre_empresa} ({ticker}): {price}"

    except requests.RequestException as e:
        return f"Error de conexión con Yahoo Finance: {e}"

    except (ValueError, KeyError) as e:
        return f"Error al procesar los datos: {e}"
