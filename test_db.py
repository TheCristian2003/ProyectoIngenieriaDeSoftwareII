from database import get_db_connection

def test_connection():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(*) as total FROM productos')
        resultado = cursor.fetchone()
        print(f"✅ Productos en la base de datos: {resultado['total']}")
        conn.close()
    else:
        print("❌ No se pudo conectar a la base de datos")

if __name__ == '__main__':
    test_connection()