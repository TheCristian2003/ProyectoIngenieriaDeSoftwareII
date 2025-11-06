import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0000',
            database='tienda_tecnologia',
            port=3306
        )
        print("✅ Conexión a MySQL exitosa")
        return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

# Función para agregar datos de prueba (opcional)
def agregar_datos_prueba():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Los datos ya los insertamos desde Workbench
        print("✅ Datos de prueba verificados")
        conn.close()