from database import get_db_connection
from carrito_db import CarritoDB

class Pedidos:
    @staticmethod
    def crear_pedido(usuario_id, direccion_envio, metodo_pago, subtotal, envio, descuento, total):
        """Crear un nuevo pedido Y ACTUALIZAR STOCK"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Generar número de pedido
                cursor.execute('SELECT generar_numero_pedido() as numero_pedido')
                numero_pedido = cursor.fetchone()['numero_pedido']
                
                # Obtener items del carrito ANTES de crear el pedido
                carrito = CarritoDB.obtener_carrito_usuario(usuario_id)
                
                # VERIFICAR STOCK ANTES DE PROCEDER
                for item in carrito:
                    cursor.execute('SELECT stock FROM productos WHERE id = %s', (item['producto_id'],))
                    producto = cursor.fetchone()
                    if not producto or producto['stock'] < item['cantidad']:
                        return False, None, f"Stock insuficiente para {item['nombre']}"

                # Crear pedido
                cursor.execute('''
                    INSERT INTO pedidos (usuario_id, numero_pedido, direccion_envio, metodo_pago, subtotal, envio, descuento, total)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (usuario_id, numero_pedido, direccion_envio, metodo_pago, subtotal, envio, descuento, total))
                
                pedido_id = cursor.lastrowid
                
                # Crear items del pedido y ACTUALIZAR STOCK
                for item in carrito:
                    # Insertar item del pedido
                    cursor.execute('''
                        INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (pedido_id, item['producto_id'], item['cantidad'], item['precio'], item['precio'] * item['cantidad']))
                    
                    # ACTUALIZAR STOCK del producto
                    cursor.execute('''
                        UPDATE productos 
                        SET stock = stock - %s 
                        WHERE id = %s
                    ''', (item['cantidad'], item['producto_id']))
                
                # Vaciar carrito después de crear pedido
                CarritoDB.vaciar_carrito(usuario_id)
                
                conn.commit()
                return True, numero_pedido, "Pedido creado exitosamente"
                
            except Exception as e:
                conn.rollback()
                return False, None, f"Error al crear pedido: {e}"
            finally:
                conn.close()
        return False, None, "Error de conexión a la base de datos"

    @staticmethod
    def obtener_pedidos_usuario(usuario_id):
        """Obtener todos los pedidos de un usuario"""
        conn = get_db_connection()
        pedidos = []
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT p.*, COUNT(pi.id) as total_items
                    FROM pedidos p
                    LEFT JOIN pedido_items pi ON p.id = pi.pedido_id
                    WHERE p.usuario_id = %s
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                ''', (usuario_id,))
                pedidos = cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener pedidos: {e}")
            finally:
                conn.close()
        return pedidos

    @staticmethod
    def obtener_detalle_pedido(pedido_id, usuario_id=None):
        """Obtener detalle completo de un pedido"""
        conn = get_db_connection()
        pedido = None
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Obtener información del pedido
                query = '''
                    SELECT p.*, u.nombre as usuario_nombre, u.email as usuario_email
                    FROM pedidos p
                    JOIN usuarios u ON p.usuario_id = u.id
                    WHERE p.id = %s
                '''
                params = [pedido_id]
                
                if usuario_id:
                    query += ' AND p.usuario_id = %s'
                    params.append(usuario_id)
                
                cursor.execute(query, params)
                pedido = cursor.fetchone()
                
                if pedido:
                    # Obtener items del pedido - CAMBIA EL NOMBRE DE LA CLAVE
                    cursor.execute('''
                        SELECT pi.*, pr.nombre, pr.imagen, pr.categoria
                        FROM pedido_items pi
                        JOIN productos pr ON pi.producto_id = pr.id
                        WHERE pi.pedido_id = %s
                    ''', (pedido_id,))
                    items_data = cursor.fetchall()  # Cambia el nombre
                    pedido['productos'] = items_data  # Usa 'productos' en lugar de 'items'
                    
            except Exception as e:
                print(f"Error al obtener detalle pedido: {e}")
            finally:
                conn.close()
        return pedido

    @staticmethod
    def obtener_todos_pedidos():
        """Obtener todos los pedidos (para admin)"""
        conn = get_db_connection()
        pedidos = []
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT p.*, u.nombre as usuario_nombre, u.email, COUNT(pi.id) as total_items
                    FROM pedidos p
                    JOIN usuarios u ON p.usuario_id = u.id
                    LEFT JOIN pedido_items pi ON p.id = pi.pedido_id
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                ''')
                pedidos = cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener todos los pedidos: {e}")
            finally:
                conn.close()
        return pedidos

    @staticmethod
    def actualizar_estado_pedido(pedido_id, nuevo_estado):
        """Actualizar estado de un pedido (para admin)"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE pedidos SET estado = %s 
                    WHERE id = %s
                ''', (nuevo_estado, pedido_id))
                conn.commit()
                return True, "Estado actualizado"
            except Exception as e:
                conn.rollback()
                return False, f"Error al actualizar estado: {e}"
            finally:
                conn.close()
        return False, "Error de conexión a la base de datos"