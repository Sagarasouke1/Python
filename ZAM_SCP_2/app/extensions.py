from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_cors import CORS
from flask import request  # Importar request desde flask para obtener la IP del cliente

# Inicializar la instancia de SQLAlchemy para manejar la base de datos
db = SQLAlchemy()

# Inicializar la instancia de Migrate para manejar las migraciones de la base de datos
migrate = Migrate()

# Inicializar la instancia de Limiter para manejar el rate limiting (limitación de tasa)
limiter = Limiter(
    key_func=lambda: request.remote_addr,  # Limitar las solicitudes según la dirección IP del cliente
    default_limits=["200 per day", "50 per hour"]  # Límites predeterminados de rate limiting
)

# Inicializar la instancia de CORS para permitir solicitudes cross-origin
cors = CORS()
