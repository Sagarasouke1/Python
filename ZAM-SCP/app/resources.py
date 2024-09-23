import logging
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime, timedelta
import pytz
from .models import User, add_user, user_exists, get_user, create_token, TokenUser, Shipment
from .utils import custom_json_serializer, error_response
from .extensions import db
from werkzeug.exceptions import Unauthorized

# Configurar logging
logging.basicConfig(filename='api_access.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Definir un Blueprint para la API y asociarlo con Flask-RESTful
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

def log_access(endpoint, token=None, success=True, message=None):
    """ Función para registrar el acceso a la API """
    username = None
    if token:
        token_record = TokenUser.query.filter_by(token=token).first()
        if token_record:
            username = token_record.username
    log_message = f"Endpoint: {endpoint} | User: {username or 'Unknown'} | Success: {success}"
    if message:
        log_message += f" | Message: {message}"
    logging.info(log_message)

def log_error(error_message, token=None):
    """ Función para registrar errores en la API """
    username = None
    if token:
        token_record = TokenUser.query.filter_by(token=token).first()
        if token_record:
            username = token_record.username
    logging.error(f"Error: {error_message} | User: {username or 'Unknown'}")

class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'password', 'company')):
            log_error("Faltan datos en el registro de usuario.")
            return {'error': 'Faltan datos. Asegúrate de proporcionar usuario, contraseña y empresa.'}, 400

        username = data['username']
        password = data['password']
        company = data['company']

        if user_exists(username):
            log_error(f"Intento de registro con un usuario ya existente: {username}")
            return {'error': 'El usuario ya existe.'}, 400

        add_user(username, password, company)
        log_access('/register', success=True, message=f"Usuario {username} registrado exitosamente.")
        return {'message': 'Usuario creado con éxito.'}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'password')):
            log_error("Faltan datos en el inicio de sesión.")
            return {'error': 'Faltan datos. Asegúrate de proporcionar usuario y contraseña.'}, 400

        username = data['username']
        password = data['password']
        user = get_user(username)

        if user is None or not user.check_password(password):
            log_error(f"Intento de inicio de sesión fallido para el usuario: {username}")
            return {'error': 'Credenciales inválidas.'}, 401

        existing_token = TokenUser.query.filter_by(username=username).first()

        if existing_token and existing_token.is_token_valid():
            expires_at_aware = existing_token.expires_at
            if expires_at_aware.tzinfo is None:
                expires_at_aware = pytz.timezone('America/Mexico_City').localize(expires_at_aware)
            
            log_access('/login', success=True, message=f"Inicio de sesión exitoso para {username}.")
            return {
                'token': existing_token.token,
                'expires_in': (expires_at_aware - datetime.now(pytz.timezone('America/Mexico_City'))).total_seconds()
            }, 200
        else:
            token = create_token(username)
            
            if existing_token:
                existing_token.token = token
                existing_token.created_at = datetime.now(pytz.timezone('America/Mexico_City'))
                existing_token.expires_at = existing_token.created_at + timedelta(days=1)
                db.session.commit()
            else:
                expiration = datetime.now(pytz.timezone('America/Mexico_City')) + timedelta(days=1)
                new_token = TokenUser(username=username, token=token, expires_at=expiration)
                db.session.add(new_token)
                db.session.commit()

            log_access('/login', success=True, message=f"Token generado para {username}.")
            return {
                'token': token,
                'expires_in': 86400
            }, 200

class ShipmentResource(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        if not token:
            log_error("Token faltante en el acceso a /shipments.")
            raise Unauthorized('Token faltante.')

        token = token.split(" ")[1]
        token_record = TokenUser.query.filter_by(token=token).first()
        if not token_record or not token_record.is_token_valid():
            log_error(f"Intento de acceso con token inválido en /shipments. Token: {token}")
            raise Unauthorized('Token inválido o expirado.')

        data = request.get_json()

        required_fields = ['operacion', 'viaje', 'area_viaje', 'carta_porte', 'factura', 'estatus_factura', 'sustituye_por']
        if not all(field in data for field in required_fields):
            log_error(f"Faltan datos en la creación de envío por {token_record.username}.")
            return {'error': 'Faltan datos. Asegúrate de proporcionar todos los campos requeridos.'}, 400

        estatus_factura = data.get('estatus_factura')

        if estatus_factura not in [1, 2, 3]:
            log_error(f"estatus_factura inválido ({estatus_factura}) en la creación de envío.")
            return {'error': 'estatus_factura debe ser 1, 2 o 3.'}, 400

        new_shipment = Shipment(
            operacion=data['operacion'],
            viaje=data['viaje'],
            area_viaje=data['area_viaje'],
            carta_porte=data['carta_porte'],
            factura=data['factura'],
            estatus_factura=estatus_factura,
            sustituye_por=data['sustituye_por']
        )

        db.session.add(new_shipment)
        db.session.commit()

        log_access('/shipments', token=token, success=True, message="Nuevo envío creado.")
        return {'message': 'Registro creado con éxito.'}, 201

# Añadir los recursos a la API
api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(ShipmentResource, '/shipments')
