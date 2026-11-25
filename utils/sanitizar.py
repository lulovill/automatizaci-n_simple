# Utilidades para el pre-procesamiento y limpieza de texto

import unicodedata

def sanitizar(nombre):
    """
    Normaliza el texto del usuario:
    - Minúsculas
    - Sin tildes
    - Sin ñ
    - Sin diéresis
    """
    nombre = nombre.lower().strip()
    
    nombre = unicodedata.normalize('NFD', nombre)

    nombre = ''.join(
        c for c in nombre
        if unicodedata.category(c) != 'Mn'
    )
  
    return nombre
