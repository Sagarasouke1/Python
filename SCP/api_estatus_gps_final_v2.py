import mysql.connector
import requests
from datetime import datetime

# Configuración de la base de datos
HOST = '10.100.1.242'
USER = 'webmaster'
PASSWORD = 'fpMvWmpYAMs^p?,H*)q+1Z]a!e^g*r'
DATABASE = 'scp_system_dev'

# Función para obtener los `id_asignacion` de la tabla `tb_api`
def obtener_id_asignaciones():
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()
    query = "SELECT id_asignacion FROM tb_api"
    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()
    return [row[0] for row in resultados]

# Función para consultar la API con el valor de `id_asignacion`
def consultar_api_metrics(id_asignacion):
    url = "http://poderonline.net/service/WebService/SCP/getMetricsCI.php"
    params = {
        'data': id_asignacion
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Función para insertar el valor de `status` y `economico` en la base de datos
def insertar_status_en_db(id_asignacion, status, economico):
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = conn.cursor()
    query = "UPDATE tb_api SET estatus_gps = %s, economico = %s WHERE id_asignacion = %s"
    cursor.execute(query, (status, economico, id_asignacion))
    conn.commit()
    conn.close()

# Función para procesar y mostrar los resultados de la API
def procesar_resultados(id_asignacion, resultado_api):
    if resultado_api.get("success") == 1:
        # Recorrer el JSON y obtener los valores de 'status' y 'economico'
        status_list = []
        economico_list = []
        if 'data' in resultado_api:
            for key, value in resultado_api['data'].items():
                if 'status' in value:
                    status_list.append(value['status'])
                if 'economico' in value:
                    economico_list.append(value['economico'])
        
        print(f"Resultado para id_asignacion {id_asignacion}:")
        for status, economico in zip(status_list, economico_list):
            print(f"Status: {status}, Economico: {economico}")
            insertar_status_en_db(id_asignacion, status, economico)
    else:
        print(f"El campo 'success' no es 1 para id_asignacion {id_asignacion}: {resultado_api.get('message', 'No se proporcionó mensaje.')}")

# Main
if __name__ == "__main__":
    try:
        # Paso 1: Obtener `id_asignacion`
        id_asignaciones = obtener_id_asignaciones()
        print("IDs de asignación obtenidos:")

        for id_asignacion in id_asignaciones:
            print(id_asignacion)

            # Paso 2: Consultar la API externa con `id_asignacion`
            resultado_api = consultar_api_metrics(id_asignacion)

            # Paso 3: Procesar y mostrar los resultados
            procesar_resultados(id_asignacion, resultado_api)

    except Exception as e:
        print(f"Error: {e}")
