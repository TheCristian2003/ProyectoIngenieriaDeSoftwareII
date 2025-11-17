from database import get_db_connection

class Categorias:
    @staticmethod
    def obtener_todas():
        """Obtener todas las categorías"""
        conn = get_db_connection()
        categorias = []
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM categorias ORDER BY nombre')
                categorias = cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener categorías: {e}")
            finally:
                conn.close()
        return categorias

    @staticmethod
    def agregar(nombre, descripcion=None):
        """Agregar nueva categoría"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO categorias (nombre, descripcion) 
                    VALUES (%s, %s)
                ''', (nombre, descripcion))
                conn.commit()
                return True, "Categoría agregada correctamente"
            except Exception as e:
                conn.rollback()
                return False, f"Error al agregar categoría: {e}"
            finally:
                conn.close()
        return False, "Error de conexión a la base de datos"

    @staticmethod
    def eliminar(categoria_id):
        """Eliminar categoría (solo si no tiene productos)"""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Verificar si hay productos en esta categoría
                cursor.execute('SELECT COUNT(*) as total FROM productos WHERE categoria = (SELECT nombre FROM categorias WHERE id = %s)', (categoria_id,))
                resultado = cursor.fetchone()
                
                if resultado[0] > 0:
                    return False, "No se puede eliminar la categoría porque tiene productos asociados"
                
                cursor.execute('DELETE FROM categorias WHERE id = %s', (categoria_id,))
                conn.commit()
                return True, "Categoría eliminada correctamente"
            except Exception as e:
                conn.rollback()
                return False, f"Error al eliminar categoría: {e}"
            finally:
                conn.close()
        return False, "Error de conexión a la base de datos"