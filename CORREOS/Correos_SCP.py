import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import mysql.connector
import os

# Configuración del servidor SMTP en CentOS 7
SMTP_SERVER = 'mail.aeo.mx'  # Cambia esto por el servidor SMTP real
SMTP_PORT = 587  # El puerto típico para el envío de correos con TLS
SMTP_USER = os.getenv('SMTP_USER')  # Usuario del correo desde variable de entorno
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # Contraseña del correo desde variable de entorno

# Conectar a la base de datos para obtener los correos por departamento
def obtener_correos_por_departamento():
    correos = {}
    try:
        conexion = mysql.connector.connect(
            host='10.100.1.242',  # Cambia esto si no es localhost
            database='scp_system_dev',
            user='webmaster',
            password='fpMvWmpYAMs^p?,H*)q+1Z]a!e^g*r'
        )
        cursor = conexion.cursor()
        query = "SELECT departamento, correo FROM tb_c_correos"
        cursor.execute(query)
        resultados = cursor.fetchall()
        for departamento, correo in resultados:
            if departamento not in correos:
                correos[departamento] = []
            correos[departamento].append(correo)
        cursor.close()
        conexion.close()
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
    return correos

# Función para enviar correos con imagen en el cuerpo
def enviar_correo_con_imagen(destinatario, asunto, mensaje_html, ruta_imagen):
    try:
        # Verificar que la imagen existe
        if not os.path.exists(ruta_imagen):
            raise FileNotFoundError(f"La imagen en la ruta '{ruta_imagen}' no existe.")

        # Crear el objeto del correo
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto

        # Cuerpo del correo en formato HTML
        msg.attach(MIMEText(mensaje_html, 'html'))

        # Leer y adjuntar la imagen al correo
        with open(ruta_imagen, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<imagen>')
            msg.attach(img)

        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        # Asegurar TLS para seguridad
        if SMTP_PORT == 587:
            server.starttls()

        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        server.quit()

        print(f"Correo enviado a {destinatario}")

    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except smtplib.SMTPAuthenticationError:
        print("Error de autenticación en el servidor SMTP.")
    except Exception as e:
        print(f"Error enviando correo: {e}")

# Función principal
def main():
    # Verificar que las credenciales SMTP están configuradas
    if not SMTP_USER or not SMTP_PASSWORD:
        print("Error: Las credenciales SMTP no están configuradas en las variables de entorno.")
        return

    correos_por_departamento = obtener_correos_por_departamento()
    for departamento, correos in correos_por_departamento.items():
        asunto = f"Información importante para el departamento {departamento}"
        
        # Mensaje HTML con una imagen incrustada
        mensaje_html = f"""
        <html>
        <body>
        <p>Este es un mensaje automático para el departamento {departamento}.</p>
        <p>Por favor, revisa la imagen adjunta:</p>
        <img src="cid:imagen" alt="Imagen adjunta" />
        </body>
        </html>
        """

        ruta_imagen = 'ruta_a_tu_imagen.jpg'  # Especifica la ruta de la imagen

        for correo in correos:
            enviar_correo_con_imagen(correo, asunto, mensaje_html, ruta_imagen)

if __name__ == "__main__":
    main()
