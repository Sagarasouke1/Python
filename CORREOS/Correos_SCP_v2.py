# -*- coding: utf-8 -*-
# Importar las librerías necesarias para enviar correos y conectarse a la base de datos
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mysql.connector

# Configuración del servidor SMTP en CentOS 7
# Este bloque define la configuración necesaria para conectarse al servidor SMTP
SMTP_SERVER = 'mail.aeo.mx'  # Dirección del servidor SMTP (modificar si es diferente)
SMTP_PORT = 25  # El puerto para enviar correos (puede cambiar según el servidor SMTP, ej: 587 para TLS)
SMTP_USER = 'scp.admin@aeo.mx'  # Dirección de correo del remitente (cambiar según el correo configurado)
SMTP_PASSWORD = 'fx;w,^1oU&-!'  # Contraseña del correo (esto debe ser almacenado de manera segura, idealmente en variables de entorno)

# Función para obtener los correos electrónicos agrupados por departamento desde la base de datos
def obtener_correos_por_departamento():
    """
    Conecta a la base de datos y obtiene los correos electrónicos, agrupados por departamento.
    Retorna un diccionario donde las llaves son los nombres de los departamentos
    y los valores son listas de correos electrónicos correspondientes a cada departamento.
    """
    correos = {}  # Diccionario para almacenar los correos agrupados por departamento
    try:
        # Conexión a la base de datos MySQL
        conexion = mysql.connector.connect(
            host='127.0.0.1',  # Dirección de la base de datos, cambiar si es necesario
            database='scp_system_dev',  # Nombre de la base de datos
            user='webmaster',  # Usuario de la base de datos
            password='W3bm4*t3r'  # Contraseña de la base de datos
        )
        cursor = conexion.cursor()  # Crear un cursor para ejecutar consultas

        # Consulta SQL para obtener los correos y departamentos
        query = "SELECT departamento, correo FROM tb_c_correos"
        cursor.execute(query)
        resultados = cursor.fetchall()  # Obtener todos los resultados de la consulta

        # Agrupar los correos por departamento
        for departamento, correo in resultados:
            if departamento not in correos:
                correos[departamento] = []  # Crear una nueva lista si el departamento no está en el diccionario
            correos[departamento].append(correo)  # Agregar el correo a la lista correspondiente
        cursor.close()  # Cerrar el cursor
        conexion.close()  # Cerrar la conexión a la base de datos
    except mysql.connector.Error as err:
        print("Error de conexión a la base de datos: {}".format(err))  # Manejar errores de conexión a la base de datos
    return correos  # Retornar el diccionario con los correos por departamento

# Función para enviar correos electrónicos sin imágenes adjuntas
def enviar_correo(destinatario, asunto, mensaje_html):
    """
    Enviar un correo electrónico utilizando el servidor SMTP configurado.
    Argumentos:
    destinatario -- dirección de correo del destinatario.
    asunto -- asunto del correo.
    mensaje_html -- contenido del correo en formato HTML.
    """
    try:
        # Crear el objeto del correo electrónico
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER  # Remitente del correo
        msg['To'] = destinatario  # Destinatario del correo
        msg['Subject'] = asunto  # Asunto del correo

        # Adjuntar el contenido del correo en formato HTML con codificación UTF-8
        msg.attach(MIMEText(mensaje_html, 'html', 'utf-8'))

        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        # Si el puerto es 587, activar TLS para mayor seguridad
        if SMTP_PORT == 587:
            server.starttls()

        # Iniciar sesión en el servidor SMTP con las credenciales configuradas
        server.login(SMTP_USER, SMTP_PASSWORD)
        # Enviar el correo electrónico
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        server.quit()  # Cerrar la conexión con el servidor SMTP

        print("Correo enviado a {}".format(destinatario))  # Confirmación de envío exitoso

    except smtplib.SMTPAuthenticationError:
        print("Error de autenticación en el servidor SMTP.")  # Manejar error de autenticación en el servidor SMTP
    except Exception as e:
        print("Error enviando correo: {}".format(e))  # Manejar otros errores durante el envío del correo

# Función para obtener el asunto y el cuerpo del mensaje según el departamento
def obtener_asunto_y_mensaje_por_departamento(departamento):
    """
    Obtener el asunto y el mensaje HTML del correo según el departamento.
    Argumento:
    departamento -- nombre del departamento para personalizar el contenido del correo.
    
    Retorna el asunto y el mensaje HTML correspondiente.
    """
    # Diccionario que contiene los mensajes personalizados para cada departamento
    mensajes_departamentos = {
        'Ventas': {
            'asunto': 'Actualización sobre las ventas del mes',  # Asunto para el departamento de Ventas
            'mensaje': """
            <html>
            <body>
            <p>Estimado equipo de ventas,</p>
            <p>Aquí están las últimas cifras de ventas del mes.</p>
            <p>¡Gracias por su esfuerzo!</p>
            </body>
            </html>
            """  # Cuerpo del mensaje en HTML para el departamento de Ventas
        },
        'Compras': {
            'asunto': 'Actualización de proveedores',  # Asunto para el departamento de Compras
            'mensaje': """
            <html>
            <body>
            <p>Estimado equipo de compras,</p>
            <p>Adjunto está la información actualizada sobre los proveedores.</p>
            <p>Saludos.</p>
            </body>
            </html>
            """  # Cuerpo del mensaje en HTML para el departamento de Compras
        },
        'Recursos Humanos': {
            'asunto': 'Nuevas políticas de la empresa',  # Asunto para el departamento de Recursos Humanos
            'mensaje': """
            <html>
            <body>
            <p>Estimado equipo de Recursos Humanos,</p>
            <p>Por favor, revisen las nuevas políticas internas de la empresa.</p>
            </body>
            </html>
            """  # Cuerpo del mensaje en HTML para Recursos Humanos
        }
        # Se pueden agregar más departamentos y mensajes personalizados aquí
    }

    # Si el departamento tiene un mensaje específico, devolverlo
    if departamento in mensajes_departamentos:
        return mensajes_departamentos[departamento]['asunto'], mensajes_departamentos[departamento]['mensaje']
    else:
        # Mensaje genérico para departamentos no especificados en el diccionario
        asunto = 'Información importante para el departamento {}'.format(departamento)
        mensaje = """
        <html>
        <body>
        <p>Este es un mensaje automático para el departamento {}.</p>
        <p>Por favor, revisa la información proporcionada en este mensaje.</p>
        </body>
        </html>
        """.format(departamento)
        return asunto, mensaje

# Función principal para la ejecución del programa
def main():
    """
    Función principal que obtiene los correos por departamento y envía un correo personalizado a cada uno.
    """
    # Verificar que las credenciales SMTP están configuradas
    if not SMTP_USER or not SMTP_PASSWORD:
        print("Error: Las credenciales SMTP no están configuradas en las variables de entorno.")
        return

    # Obtener los correos electrónicos agrupados por departamento desde la base de datos
    correos_por_departamento = obtener_correos_por_departamento()
    
    # Iterar por cada departamento y sus correos correspondientes
    for departamento, correos in correos_por_departamento.items():
        # Obtener el asunto y el cuerpo del mensaje específicos para cada departamento
        asunto, mensaje_html = obtener_asunto_y_mensaje_por_departamento(departamento)

        # Enviar el correo a cada dirección de correo en la lista del departamento
        for correo in correos:
            enviar_correo(correo, asunto, mensaje_html)

# Ejecutar la función principal solo si se ejecuta este archivo directamente
if __name__ == "__main__":
    main()
