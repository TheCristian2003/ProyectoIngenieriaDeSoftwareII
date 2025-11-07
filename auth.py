from database import get_db_connection
import hashlib

class Auth:
    @staticmethod
    def hash_password(password):
        """Hashear contraseña para seguridad"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        """Verificar contraseña"""
        return Auth.hash_password(password) == hashed
    
    @staticmethod
    def register_user(email, password, nombre, apellido=None, telefono=None):
        """Registrar nuevo usuario"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Verificar si el email ya existe
                cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
                if cursor.fetchone():
                    return False, "El email ya está registrado"
                
                # Hashear password
                hashed_password = Auth.hash_password(password)
                
                # Insertar nuevo usuario
                cursor.execute('''
                    INSERT INTO usuarios (email, password, nombre, apellido, telefono, rol)
                    VALUES (%s, %s, %s, %s, %s, 'cliente')
                ''', (email, hashed_password, nombre, apellido, telefono))
                
                conn.commit()
                conn.close()
                return True, "Usuario registrado exitosamente"
                
            except Exception as e:
                conn.close()
                return False, f"Error al registrar usuario: {e}"
        return False, "Error de conexión a la base de datos"
    
    @staticmethod
    def login_user(email, password):
        """Iniciar sesión de usuario"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Buscar usuario
                cursor.execute('''
                    SELECT id, email, password, nombre, apellido, rol 
                    FROM usuarios 
                    WHERE email = %s AND activo = TRUE
                ''', (email,))
                
                user = cursor.fetchone()
                if user and Auth.verify_password(password, user['password']):
                    # Actualizar último login
                    cursor.execute('UPDATE usuarios SET ultimo_login = NOW() WHERE id = %s', (user['id'],))
                    conn.commit()
                    conn.close()
                    return True, user
                else:
                    conn.close()
                    return False, "Email o contraseña incorrectos"
                    
            except Exception as e:
                conn.close()
                return False, f"Error al iniciar sesión: {e}"
        return False, "Error de conexión a la base de datos"
    
    @staticmethod
    def get_user_by_id(user_id):
        """Obtener usuario por ID"""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT id, email, nombre, apellido, telefono, rol, created_at
                FROM usuarios WHERE id = %s
            ''', (user_id,))
            user = cursor.fetchone()
            conn.close()
            return user
        return None

    @staticmethod
    def get_all_users():
        """Obtener todos los usuarios (para admin)"""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT id, email, nombre, apellido, telefono, rol, activo, created_at, ultimo_login
                FROM usuarios ORDER BY created_at DESC
            ''')
            users = cursor.fetchall()
            conn.close()
            return users
        return []