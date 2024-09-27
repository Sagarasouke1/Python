from datetime import datetime, timedelta
import pytz
import jwt
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

class User(db.Model):
    """
    Modelo de usuario para manejar la autenticación.
    """
    __tablename__ = 'tb_acceso_apis'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('America/Mexico_City')))

    def set_password(self, password):
        """
        Genera un hash de la contraseña y lo almacena en el atributo password_hash.
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.
        """
        return check_password_hash(self.password_hash, password)

class TokenUser(db.Model):
    """
    Modelo para almacenar tokens de autenticación de usuarios y su fecha de caducidad.
    """
    __tablename__ = 'tb_token_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    token = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('America/Mexico_City')))
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_token_valid(self):
        """
        Verifica si el token es válido comparando la fecha de expiración con la fecha actual.
        """
        current_time = datetime.now(pytz.timezone('America/Mexico_City'))
        if self.expires_at.tzinfo is None:
            expires_at_aware = pytz.timezone('America/Mexico_City').localize(self.expires_at)
        else:
            expires_at_aware = self.expires_at
        return current_time < expires_at_aware

class Shipment(db.Model):
    """
    Modelo para representar envíos de la base de datos.
    """
    __tablename__ = 'tb_shipment'

    id = db.Column(db.Integer, primary_key=True)
    operacion = db.Column(db.Integer, nullable=False)
    descripcion_operacion = db.Column(db.Text, nullable=True, default='')
    viaje = db.Column(db.Integer, nullable=False)
    area_viaje = db.Column(db.Integer, nullable=False)
    carta_porte = db.Column(db.Text, nullable=False)
    factura = db.Column(db.Text, nullable=False)
    estatus_factura = db.Column(db.Integer, nullable=False)
    descripcion_estatus = db.Column(db.Text, nullable=True, default='')
    sustituye_por = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('America/Mexico_City')))

    # Diccionarios para describir los tipos de operación y los estados de la factura
    OPERACION_DESCRIPCIONES = {
        1: "Domestico Gdl",
        2: "Import -Export",
        3: "Maritimo",
        4: "Dedicados Ryder",
        5: "Domestico Mex",
        6: "Dedicados BF",
        7: "Dedicados Amazon",
        8: "Dedicados Walmart",
        9: "Dedicados",
        10: "Dedicados Toyota",
        11: "Dedicados Philip",
        12: "Dedicados Cuervo"
    }

    ESTATUS_FACTURA_DESCRIPCIONES = {
        1: "Facturado",
        2: "Cancelado",
        3: "Refacturado/Sustitucion"
    }

    def __init__(self, operacion, viaje, area_viaje, carta_porte, factura, estatus_factura, sustituye_por, descripcion_operacion=None, descripcion_estatus=None):
        """
        Constructor de la clase Shipment que inicializa los valores proporcionados.
        """
        self.operacion = operacion
        self.descripcion_operacion = self.OPERACION_DESCRIPCIONES.get(operacion, '') if not descripcion_operacion else descripcion_operacion
        self.viaje = viaje
        self.area_viaje = area_viaje
        self.carta_porte = carta_porte
        self.factura = factura
        self.estatus_factura = estatus_factura
        self.descripcion_estatus = self.ESTATUS_FACTURA_DESCRIPCIONES.get(estatus_factura, '') if not descripcion_estatus else descripcion_estatus
        self.sustituye_por = sustituye_por
        self.created_at = datetime.now(pytz.timezone('America/Mexico_City'))

# Funciones relacionadas con el modelo User
def add_user(username, password, company):
    """
    Crea y agrega un nuevo usuario en la base de datos.
    """
    user = User(username=username, company=company)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def get_user(username):
    """
    Busca y devuelve un usuario por su nombre de usuario.
    """
    return User.query.filter_by(username=username).first()

def user_exists(username):
    """
    Verifica si un usuario con el nombre proporcionado ya existe en la base de datos.
    """
    return get_user(username) is not None

def create_token(username):
    """
    Crea un nuevo token JWT para el usuario y lo devuelve.
    """
    expiration = datetime.now(pytz.timezone('America/Mexico_City')) + timedelta(days=1)
    token = jwt.encode({'username': username, 'exp': expiration}, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token
