from flask import Flask
from app.routes import api_bp

def create_app():
    try:
        app = Flask(__name__)
        app.register_blueprint(api_bp, url_prefix='/api')
        return app
    except Exception as e:
        print(f"Error al crear la aplicación: {e}")
        raise

