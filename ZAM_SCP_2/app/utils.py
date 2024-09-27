from datetime import datetime
from flask import jsonify

def custom_json_serializer(obj):
    """
    Serializa objetos de tipo datetime a una cadena de texto con el formato 'YYYY-MM-DD HH:MM:SS'.
    Si el objeto no es de tipo datetime, lanza un TypeError.

    Args:
        obj: El objeto que se quiere serializar.

    Returns:
        Una cadena de texto que representa el datetime en el formato 'YYYY-MM-DD HH:MM:SS'.

    Raises:
        TypeError: Si el objeto no es de tipo datetime.
    """
    if isinstance(obj, datetime):
        # Convertir el objeto datetime a una cadena en el formato deseado
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    # Si el objeto no es serializable, lanzar un error
    raise TypeError("Type not serializable")

def error_response(message, status_code):
    """
    Crea una respuesta de error en formato JSON con un mensaje y un código de estado HTTP.

    Args:
        message: El mensaje de error a incluir en la respuesta.
        status_code: El código de estado HTTP a devolver.

    Returns:
        Un objeto de respuesta JSON que contiene el mensaje de error y el código de estado.
    """
    # Crear un diccionario con el mensaje de error
    response_content = {'error': message}
    # Convertir el diccionario a una respuesta JSON
    response = jsonify(response_content)
    # Asignar el código de estado HTTP a la respuesta
    response.status_code = status_code
    return response
