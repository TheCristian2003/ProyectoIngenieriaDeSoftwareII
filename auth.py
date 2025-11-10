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
    
    
    @staticmethod
    def update_user_profile(user_id, nombre, apellido, telefono):
        """Actualizar perfil de usuario"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE usuarios 
                    SET nombre = %s, apellido = %s, telefono = %s 
                    WHERE id = %s
                ''', (nombre, apellido, telefono, user_id))
                conn.commit()
                conn.close()
                return True, "Perfil actualizado exitosamente"
            except Exception as e:
                conn.close()
                return False, f"Error al actualizar perfil: {e}"
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Cambiar contraseña de usuario"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Verificar contraseña actual
                cursor.execute('SELECT password FROM usuarios WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                
                if user and Auth.verify_password(current_password, user['password']):
                    # Actualizar contraseña
                    new_hashed_password = Auth.hash_password(new_password)
                    cursor.execute('UPDATE usuarios SET password = %s WHERE id = %s', 
                                 (new_hashed_password, user_id))
                    conn.commit()
                    conn.close()
                    return True, "Contraseña cambiada exitosamente"
                else:
                    conn.close()
                    return False, "La contraseña actual es incorrecta"
                    
            except Exception as e:
                conn.close()
                return False, f"Error al cambiar contraseña: {e}"
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def get_user_addresses(user_id):
        """Obtener direcciones del usuario"""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT * FROM direcciones 
                WHERE usuario_id = %s 
                ORDER BY es_principal DESC, created_at DESC
            ''', (user_id,))
            addresses = cursor.fetchall()
            conn.close()
            return addresses
        return []

    @staticmethod
    def add_user_address(user_id, nombre, direccion, ciudad, codigo_postal, telefono_contacto, es_principal=False):
        """Agregar nueva dirección para usuario"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Si es principal, quitar principal de otras direcciones
                if es_principal:
                    cursor.execute('UPDATE direcciones SET es_principal = FALSE WHERE usuario_id = %s', (user_id,))
                
                cursor.execute('''
                    INSERT INTO direcciones (usuario_id, nombre, direccion, ciudad, codigo_postal, telefono_contacto, es_principal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (user_id, nombre, direccion, ciudad, codigo_postal, telefono_contacto, es_principal))
                
                conn.commit()
                conn.close()
                return True, "Dirección agregada exitosamente"
            except Exception as e:
                conn.close()
                return False, f"Error al agregar dirección: {e}"
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def delete_user_address(address_id, user_id):
        """Eliminar dirección del usuario"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM direcciones WHERE id = %s AND usuario_id = %s', (address_id, user_id))
                conn.commit()
                conn.close()
                return True, "Dirección eliminada exitosamente"
            except Exception as e:
                conn.close()
                return False, f"Error al eliminar dirección: {e}"
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def set_primary_address(address_id, user_id):
        """Establecer dirección como principal"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Quitar principal de todas las direcciones
                cursor.execute('UPDATE direcciones SET es_principal = FALSE WHERE usuario_id = %s', (user_id,))
                
                # Establecer nueva dirección como principal
                cursor.execute('UPDATE direcciones SET es_principal = TRUE WHERE id = %s AND usuario_id = %s', 
                             (address_id, user_id))
                
                conn.commit()
                conn.close()
                return True, "Dirección principal actualizada"
            except Exception as e:
                conn.close()
                return False, f"Error al actualizar dirección principal: {e}"
        return False, "Error de conexión a la base de datos"