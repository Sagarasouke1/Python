from flask import Flask
from config import Config
from .extensions import db, migrate, limiter, cors
from .resources import api_bp

def create_app():
    """
    Fábrica de aplicaciones Flask que inicializa y configura todas las extensiones necesarias.
    """
    # Crear la instancia de la aplicación Flask
    app = Flask(__name__)
    
    # Cargar la configuración de la aplicación desde el archivo de configuración
    app.config.from_object(Config)

    # Inicializar las extensiones con la aplicación
    db.init_app(app)  # Inicializa la extensión SQLAlchemy para manejar la base de datos
    migrate.init_app(app, db)  # Inicializa la extensión Flask-Migrate para manejar migraciones de la base de datos
    limiter.init_app(app)  # Inicializa Flask-Limiter para manejar límites de tasa (rate limiting)
    cors.init_app(app)  # Inicializa Flask-CORS para habilitar CORS en todas las rutas de la API

    # Registrar el Blueprint de la API con un prefijo de URL
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Crear todas las tablas de la base de datos si aún no existen (útil en desarrollo)
    with app.app_context():
        db.create_all()

    # Devolver la instancia de la aplicación Flask configurada y lista para ejecutarse
    return app
