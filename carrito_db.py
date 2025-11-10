from database import get_db_connection

class CarritoDB:
    @staticmethod
    def obtener_carrito_usuario(usuario_id):
        """Obtener carrito del usuario desde la base de datos"""
        conn = get_db_connection()
        carrito = []
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT c.*, p.nombre, p.precio, p.imagen, p.categoria, p.stock
                    FROM carritos c
                    JOIN productos p ON c.producto_id = p.id
                    WHERE c.usuario_id = %s
                    ORDER BY c.created_at DESC
                ''', (usuario_id,))
                carrito = cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener carrito: {e}")
            finally:
                conn.close()
        return carrito

    @staticmethod
    def agregar_al_carrito(usuario_id, producto_id, cantidad=1):
        """Agregar producto al carrito en la base de datos"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Verificar si ya existe en el carrito
                cursor.execute('''
                    SELECT id, cantidad FROM carritos 
                    WHERE usuario_id = %s AND producto_id = %s
                ''', (usuario_id, producto_id))
                
                item_existente = cursor.fetchone()
                
                if item_existente:
                    # Actualizar cantidad
                    nueva_cantidad = item_existente[1] + cantidad
                    cursor.execute('''
                        UPDATE carritos SET cantidad = %s 
                        WHERE usuario_id = %s AND producto_id = %s
                    ''', (nueva_cantidad, usuario_id, producto_id))
                else:
                    # Insertar nuevo item
                    cursor.execute('''
                        INSERT INTO carritos (usuario_id, producto_id, cantidad)
                        VALUES (%s, %s, %s)
                    ''', (usuario_id, producto_id, cantidad))
                
                conn.commit()
                return True, "Producto agregado al carrito"
                
            except Exception as e:
                conn.rollback()
                return False, f"Error al agregar al carrito: {e}"
            finally:
                conn.close()
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def actualizar_cantidad(usuario_id, producto_id, nueva_cantidad):
        """Actualizar cantidad de producto en el carrito"""
        if nueva_cantidad <= 0:
            return CarritoDB.eliminar_del_carrito(usuario_id, producto_id)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE carritos SET cantidad = %s 
                    WHERE usuario_id = %s AND producto_id = %s
                ''', (nueva_cantidad, usuario_id, producto_id))
                conn.commit()
                return True, "Cantidad actualizada"
            except Exception as e:
                conn.rollback()
                return False, f"Error al actualizar cantidad: {e}"
            finally:
                conn.close()
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def eliminar_del_carrito(usuario_id, producto_id):
        """Eliminar producto del carrito"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM carritos 
                    WHERE usuario_id = %s AND producto_id = %s
                ''', (usuario_id, producto_id))
                conn.commit()
                return True, "Producto eliminado del carrito"
            except Exception as e:
                conn.rollback()
                return False, f"Error al eliminar del carrito: {e}"
            finally:
                conn.close()
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def vaciar_carrito(usuario_id):
        """Vaciar todo el carrito del usuario"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM carritos WHERE usuario_id = %s', (usuario_id,))
                conn.commit()
                return True, "Carrito vaciado"
            except Exception as e:
                conn.rollback()
                return False, f"Error al vaciar carrito: {e}"
            finally:
                conn.close()
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def obtener_contador_carrito(usuario_id):
        """Obtener cantidad total de items en el carrito"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT SUM(cantidad) as total 
                    FROM carritos 
                    WHERE usuario_id = %s
                ''', (usuario_id,))
                resultado = cursor.fetchone()
                return resultado[0] or 0
            except Exception as e:
                print(f"Error al obtener contador: {e}")
                return 0
            finally:
                conn.close()
        return 0