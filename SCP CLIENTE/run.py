from app import create_app
from config import Config  # Importar la clase Config

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)  # Usar la variable DEBUG desde la configuración
