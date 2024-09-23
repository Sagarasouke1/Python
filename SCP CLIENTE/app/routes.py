from flask import Blueprint, jsonify, request
from app.database import get_db_connection

# Definir el blueprint para la API
api_bp = Blueprint('api', __name__)

@api_bp.route('/viaje', methods=['GET'])
def get_viaje_info():
    id_viaje = request.args.get('id_viaje')

    if not id_viaje:
        return jsonify({"error": "Falta el parámetro 'id_viaje'"}), 400

    try:
        # Establecer conexión a la base de datos
        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        
        with connection.cursor(dictionary=True) as cursor:
            # Consulta SQL para obtener la información del viaje y del GPS
            query = """
                SELECT 
                    v.Viaje, v.carta_porte, v.no_embarque, v.operador, 
                    v.tracto, v.remolque, v.ruta, v.llegada_carga_ci, v.llegada_descarga_ci,
                    g.economico, g.estatus_gps, g.tipo, g.latitude, g.longitude
                FROM vista_operaciones v
                JOIN V_GPS_AEO g ON v.Viaje = g.n_viaje
                WHERE v.Viaje = %s
            """
            
            # Ejecutar la consulta, asegurando que el parámetro se pase como una tupla
            cursor.execute(query, (id_viaje,))
            results = cursor.fetchall()
            
            if not results:
                return jsonify({"error": "No se encontró el viaje con ese ID"}), 404
            
            # Construir la respuesta JSON según la estructura solicitada
            viaje_info = {
                "viaje": {
                    "Viaje": results[0]['Viaje'],
                    "carta_porte": results[0]['carta_porte'],
                    "no_embarque": results[0]['no_embarque'],
                    "operador": results[0]['operador'],
                    "remolque": results[0]['remolque'],
                    "tracto": results[0]['tracto'],
                    "ruta": results[0]['ruta'],
                    "llegada_carga_ci": results[0]['llegada_carga_ci'],
                    "llegada_descarga_ci": results[0]['llegada_descarga_ci']
                },
                "gps": []
            }

            # Agregar los detalles de GPS según la estructura solicitada, evitando repeticiones
            gps_data = []
            for row in results:
                gps_entry = {
                    "economico": row['economico'],
                    "estatus_gps": row['estatus_gps'],
                    "tipo": row['tipo'],
                    "posicion": {
                        "Longitud": row['longitude'] if row['longitude'] else "",
                        "Latitud": row['latitude'] if row['latitude'] else ""
                    }
                }
                gps_data.append(gps_entry)
            
            viaje_info['gps'] = gps_data
            
            return jsonify(viaje_info)
    
    except Exception as e:
        # Mostrar el error en la consola y devolverlo en la respuesta
        print(f"Error en la consulta SQL o en la conexión: {e}")
        return jsonify({"error": f"Error en la consulta SQL o en la conexión: {e}"}), 500

    finally:
        # Asegurarse de que la conexión se cierra
        if connection:
            connection.close()
