from auth import Auth

# Probar el hashing
password = "admin123"
hashed = Auth.hash_password(password)
print(f"Password: {password}")
print(f"Hash: {hashed}")
print(f"Verificación: {Auth.verify_password('admin123', hashed)}")

# Probar con un usuario específico
from database import get_db_connection

def debug_user(email):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT email, password FROM usuarios WHERE email = %s', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            print(f"\nUsuario: {user['email']}")
            print(f"Hash en BD: {user['password']}")
            print(f"Verificación con 'admin123': {Auth.verify_password('admin123', user['password'])}")
        else:
            print(f"Usuario {email} no encontrado")

debug_user('admin@techstore.com')