import mysql.connector
import requests
from datetime import datetime
import time

# Configuración de la base de datos
DB_CONFIG_DEV = {
    'host': '10.100.1.242',
    'user': 'webmaster',
    'password': 'fpMvWmpYAMs^p?,H*)q+1Z]a!e^g*r',
    'database': 'scp_system_dev'
}

DB_CONFIG_V3 = {
    'host': '10.100.1.242',
    'user': 'webmaster',
    'password': 'fpMvWmpYAMs^p?,H*)q+1Z]a!e^g*r',
    'database': 'scp_system_v3'
}

# Función para consultar la API con el ci y type
def consultar_api(ci, type_value):
    url = "https://skymeduza.com/aplicacion/servicio/webService/SCP/get_asign_route.php"
    params = {
        'ci': ci,
        'type': type_value,
        'enviroment': 'productivo'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Levantar excepción si la solicitud falla
    return response.json()

# Función para extraer id_asignacion de las claves que comienzan con "ORIEN"
def extraer_id_asignacion_carga_descarga(json_data):
    if json_data.get("success") != 1:
        return []

    return [
        (item.get("id_asignacion"), item.get("tipo"))
        for key, items in json_data.get("data", {}).items()
        if "ORIEN" in key
        for item in items
    ]

# Función para verificar si el registro ya existe en la base de datos
def registro_existe(cursor, id_asignacion, n_viaje, table_name):
    query = f"""
        SELECT 1 FROM {table_name}
        WHERE id_asignacion = %s AND n_viaje = %s
        LIMIT 1
    """
    cursor.execute(query, (id_asignacion, n_viaje))
    return cursor.fetchone() is not None

# Función para truncar la tabla antes de insertar nuevos datos
def truncate_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    conn.commit()

# Función para guardar el resultado en la base de datos
def guardar_resultado_en_db(cursor, id_carta, n_viaje, asignaciones, table_name):
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for id_asignacion, tipo in asignaciones:
        if not registro_existe(cursor, id_asignacion, n_viaje, table_name):
            cursor.execute(f'''
                INSERT INTO {table_name} (id_ci, id_asignacion, n_viaje, tipo, registro)
                VALUES (%s, %s, %s, %s, %s)
            ''', (id_carta, id_asignacion, n_viaje, tipo, fecha_actual))

# Función para obtener los id_carta con estado "Aceptadas" de diferentes tablas en scp_system_v3
def obtener_id_carta_aceptadas(cursor, tabla, columna_id_carta, columna_n_viaje):
    query = f"""
        SELECT {columna_id_carta}, {columna_n_viaje}
        FROM {tabla}
        WHERE DATE(aceptacion) BETWEEN DATE_SUB(CURDATE(), INTERVAL 3 DAY) AND DATE_SUB(CURDATE(), INTERVAL 1 DAY)
    """
    cursor.execute(query)
    return cursor.fetchall()

# Main
if __name__ == "__main__":
    start_time = time.time()  # Marca de tiempo inicial

    try:
        tablas = [
            ('tb_carta_dom_p', 'DOM', 'tb_api', 'id_carta_dom', 'n_viaje'),
            ('tb_carta_ie_p', 'IE', 'tb_api', 'id_carta_ie', 'n_viaje'),
            ('tb_carta_mar_p', 'MAR', 'tb_api', 'id_carta_mar', 'n_viaje'),
            ('tb_carta_dommt_p', 'DOMMT', 'tb_api', 'id_carta_dommt', 'n_viaje')
        ]

        # Conexión a la base de datos de desarrollo
        conn_dev = mysql.connector.connect(**DB_CONFIG_DEV)
        cursor_dev = conn_dev.cursor()

        # Conexión a la base de datos scp_system_v3
        conn_v3 = mysql.connector.connect(**DB_CONFIG_V3)
        cursor_v3 = conn_v3.cursor()

        # Truncar la tabla antes de comenzar a insertar los nuevos registros
        truncate_table(conn_dev, 'tb_api')

        for tabla, tipo, tabla_destino, columna_id_carta, columna_n_viaje in tablas:
            print(f"Procesando tabla {tabla} con tipo {tipo}")

            # Paso 1: Obtener id_carta aceptadas desde la base de datos scp_system_v3
            ids_aceptadas = obtener_id_carta_aceptadas(cursor_v3, tabla, columna_id_carta, columna_n_viaje)
            print(f"IDs de carta con estado 'Aceptada' en {tabla}:")

            for id_carta, n_viaje in ids_aceptadas:
                print(f"ID Carta: {id_carta}, Número de Viaje: {n_viaje}")
                
                # Paso 2: Consultar la API con ci igual a id_carta y el tipo correspondiente
                resultado_api = consultar_api(id_carta, tipo)
                
                # Paso 3: Extraer id_asignacion del JSON de respuesta
                id_asignaciones = extraer_id_asignacion_carga_descarga(resultado_api)
                
                # Paso 4: Guardar el resultado en la base de datos de desarrollo
                guardar_resultado_en_db(cursor_dev, id_carta, n_viaje, id_asignaciones, tabla_destino)
                
                print(f"ID_asignaciones para ID {id_carta} en {tabla}:")
                for id_asignacion, tipo_asignacion in id_asignaciones:
                    print(f"ID Asignación: {id_asignacion}, Tipo: {tipo_asignacion}")

        conn_dev.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor_v3.close()
        conn_v3.close()
        cursor_dev.close()
        conn_dev.close()

    end_time = time.time()  # Marca de tiempo final
    elapsed_time = end_time - start_time  # Tiempo total de ejecución
    print(f"Tiempo de ejecución del script: {elapsed_time:.2f} segundos")
