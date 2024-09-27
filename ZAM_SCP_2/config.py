import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """
    Clase de configuración para la aplicación Flask.
    Carga y organiza las variables de entorno necesarias para configurar la aplicación.
    """

    # Construir la URI de la base de datos utilizando las variables de entorno
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    
    # Desactivar la característica de seguimiento de modificaciones para mejorar el rendimiento
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clave secreta utilizada para la seguridad de la aplicación, como la protección de sesiones y JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Valor predeterminado si no se configura en .env

    # Opciones del motor SQLAlchemy para optimizar la conexión a la base de datos
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Verifica la conexión antes de usarla para evitar desconexiones inesperadas
        "pool_recycle": 1800    # Recicla (restablece) las conexiones cada 30 minutos para mantenerlas frescas
    }

    # Configuraciones de CORS (Cross-Origin Resource Sharing)
    CORS_HEADERS = 'Content-Type'  # Define los encabezados permitidos en solicitudes CORS

    # Configuración de límites de tasa (rate limiting) para controlar la cantidad de solicitudes permitidas
    RATE_LIMIT = os.getenv('RATE_LIMIT', '200 per day;50 per hour')  # Valor predeterminado si no se configura en .env
