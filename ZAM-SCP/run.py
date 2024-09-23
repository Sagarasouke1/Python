from app import create_app

# Crear una instancia de la aplicación Flask usando la fábrica create_app
app = create_app()

if __name__ == '__main__':
    """
    Este bloque de código se ejecuta solo si el script se ejecuta directamente (no si es importado como módulo).
    """
    # Ejecutar la aplicación Flask en modo debug para desarrollo.
    # El modo debug permite el auto-reload de la aplicación cuando se hacen cambios en el código,
    # y también proporciona una interfaz interactiva de depuración en caso de errores.
    app.run(debug=True)


