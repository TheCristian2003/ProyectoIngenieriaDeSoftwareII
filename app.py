from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from database import get_db_connection
from auth import Auth
import os
import time
import threading
import requests
from werkzeug.utils import secure_filename
from carrito_db import CarritoDB
from pedidos import Pedidos
from categorias import Categorias

app = Flask(__name__)
app.secret_key = 'techstore_secret_key_2024'  # Clave para las sesiones

# Configuración para subida de archivos
app.config['UPLOAD_FOLDER'] = 'static/images/productos'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB máximo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           

# =============================================
# KEEP ALIVE SYSTEM
# =============================================

@app.route('/health')
def health_check():
    """Endpoint simple para health checks - Mantiene activo el servicio"""
    return jsonify({
        'status': 'healthy',
        'service': 'TechStore',
        'timestamp': time.time(),
        'message': 'Service is running smoothly'
    }), 200

@app.route('/api/status')
def status_check():
    """Endpoint más detallado para monitoreo completo"""
    try:
        # Verificar base de datos
        conn = get_db_connection()
        db_status = 'connected' if conn else 'disconnected'
        db_message = 'Database connection successful' if conn else 'Database connection failed'
        
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT COUNT(*) as total FROM productos')
            product_count = cursor.fetchone()['total']
            conn.close()
        else:
            product_count = 0
        
        return jsonify({
            'status': 'operational',
            'database': {
                'status': db_status,
                'message': db_message,
                'product_count': product_count
            },
            'timestamp': time.time(),
            'service': 'TechStore Flask App',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'error': str(e),
            'timestamp': time.time()
        }), 500

def start_keep_alive():
    """Inicia el thread de keep-alive en segundo plano"""
    def ping_self():
        # Obtener la URL dinámicamente o usar una por defecto
        app_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://tu-app.onrender.com')
        
        while True:
            try:
                response = requests.get(f"{app_url}/health", timeout=10)
                print(f"✅ Auto-ping exitoso ({response.status_code}): {time.strftime('%Y-%m-%d %H:%M:%S')}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error en auto-ping: {e}")
            except Exception as e:
                print(f"⚠️  Error inesperado en keep-alive: {e}")
            
            # Esperar 8 minutos (menos de 15 para evitar que se duerma)
            time.sleep(480)  # 8 minutos
    
    # Solo activar en producción (Render)
    if os.environ.get("RENDER") == "True":
        thread = threading.Thread(target=ping_self)
        thread.daemon = True  # Esto hace que el thread se cierre cuando la app principal se cierre
        thread.start()
        print("🟢 Keep-alive system activated")



@app.route('/')
def index():
    conn = get_db_connection()
    productos_destacados = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos LIMIT 4')  # Solo 4 productos en inicio
        productos_destacados = cursor.fetchall()
        conn.close()
    
    return render_template('home.html', productos=productos_destacados)

@app.route('/productos')
def productos():
    conn = get_db_connection()
    todos_productos = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos')
        todos_productos = cursor.fetchall()
        conn.close()
    
    return render_template('productos.html', productos=todos_productos)

@app.route('/api/productos')
def api_productos():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos')
        productos = cursor.fetchall()
        conn.close()
        return jsonify(productos)
    return jsonify([])


@app.route('/api/productos/<int:producto_id>')
def api_producto_individual(producto_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        conn.close()
        if producto:
            return jsonify(producto)
    return jsonify({'error': 'Producto no encontrado'}), 404


@app.route('/carrito')
def carrito():
    return render_template('carrito.html')


# Ruta para buscar productos (API)
@app.route('/api/buscar-productos')
def api_buscar_productos():
    query = request.args.get('q', '')
    categoria = request.args.get('categoria', '')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM productos WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (nombre LIKE %s OR descripcion LIKE %s)"
            params.extend([f'%{query}%', f'%{query}%'])
        
        if categoria:
            sql += " AND categoria = %s"
            params.append(categoria)
        
        cursor.execute(sql, params)
        productos = cursor.fetchall()
        conn.close()
        return jsonify(productos)
    
    return jsonify([])

# Ruta para agregar datos de prueba (si necesitas más productos)
@app.route('/agregar-mas-datos')
def agregar_mas_datos():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        productos_extra = [
            ('Mouse Gaming RGB', 'Mouse ergonómico 6400DPI, 7 botones', 45.00, 'Periféricos', 30, 'mouse_gaming.jpg'),
            ('Auriculares Gaming', 'Sonido surround 7.1, micrófono retráctil', 65.00, 'Periféricos', 15, 'auriculares_gaming.jpg'),
            ('CPU Cooler Air', 'Doble ventilador, RGB, soporte LGA1700', 55.00, 'Refrigeración', 25, 'cooler_air.jpg'),
            ('Disco Duro 2TB', 'HDD 3.5", 7200RPM, SATA III', 75.00, 'Almacenamiento', 12, 'hdd_2tb.jpg')
        ]
        
        cursor.executemany('''
            INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', productos_extra)
        
        conn.commit()
        conn.close()
        return 'Datos extra agregados correctamente'
    
    return 'Error al agregar datos'


# Rutas de autenticación
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        apellido = request.form.get('apellido', '')
        telefono = request.form.get('telefono', '')
        
        success, message = Auth.register_user(email, password, nombre, apellido, telefono)
        
        if success:
            # Iniciar sesión automáticamente después del registro
            success_login, user = Auth.login_user(email, password)
            if success_login:
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session['user_nombre'] = user['nombre']
                session['user_rol'] = user['rol']
                return redirect('/')
            else:
                return render_template('registro.html', error=message)
        else:
            return render_template('registro.html', error=message)
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        success, result = Auth.login_user(email, password)
        
        if success:
            user = result
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_nombre'] = user['nombre']
            session['user_rol'] = user['rol']
            return redirect('/')
        else:
            return render_template('login.html', error=result)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Decorador para rutas que requieren login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Decorador para rutas que requieren ser admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        if session.get('user_rol') != 'admin':
            return "Acceso denegado. Se requiere permisos de administrador.", 403
        return f(*args, **kwargs)
    return decorated_function


# =============================================
# RUTAS DE ADMINISTRACIÓN
# =============================================

# Dashboard de administración
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    stats = {}
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) as total FROM usuarios')
        stats['total_usuarios'] = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM productos')
        stats['total_productos'] = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM usuarios WHERE rol = "admin"')
        stats['total_admins'] = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM usuarios WHERE created_at >= CURDATE()')
        stats['usuarios_hoy'] = cursor.fetchone()['total']
        
        # Productos con stock bajo
        cursor.execute('SELECT COUNT(*) as total FROM productos WHERE stock < 10')
        stats['stock_bajo'] = cursor.fetchone()['total']
        
        conn.close()
    
    return render_template('admin/dashboard.html', stats=stats)

# Gestión de usuarios
@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    users = Auth.get_all_users()
    return render_template('admin/usuarios.html', users=users)

# Gestión de productos
@app.route('/admin/productos')
@admin_required
def admin_productos():
    conn = get_db_connection()
    productos = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, stock, imagen, created_at 
            FROM productos ORDER BY created_at DESC
        ''')
        productos = cursor.fetchall()
        conn.close()
    
    return render_template('admin/productos.html', productos=productos)

# Agregar nuevo producto
@app.route('/admin/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_nuevo_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        categoria = request.form['categoria']
        stock = int(request.form['stock'])
        
        # Manejar la imagen
        imagen = 'default.png'  # Valor por defecto
        
        # Verificar si se subió un archivo
        if 'archivo_imagen' in request.files:
            file = request.files['archivo_imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Guardar el archivo
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagen = filename
            else:
                # Si no se subió archivo, usar el nombre manual
                imagen = request.form.get('imagen', 'default.png')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombre, descripcion, precio, categoria, stock, imagen))
            
            conn.commit()
            conn.close()
            return redirect('/admin/productos')
    
    categorias = Categorias.obtener_todas()
    return render_template('admin/nuevo_producto.html', categorias=categorias)

# Editar producto
@app.route('/admin/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
@admin_required
def admin_editar_producto(producto_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        categoria = request.form['categoria']
        stock = int(request.form['stock'])
        
        # Manejar la imagen
        nueva_imagen = request.form.get('imagen', '')
        
        # Verificar si se subió un archivo nuevo
        if 'archivo_imagen' in request.files:
            file = request.files['archivo_imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Guardar el nuevo archivo
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                nueva_imagen = filename
        
        if conn:
            cursor = conn.cursor()
            # Siempre actualizar la imagen (puede ser la misma o una nueva)
            cursor.execute('''
                UPDATE productos 
                SET nombre=%s, descripcion=%s, precio=%s, categoria=%s, stock=%s, imagen=%s
                WHERE id=%s
            ''', (nombre, descripcion, precio, categoria, stock, nueva_imagen, producto_id))
            
            conn.commit()
            conn.close()
            return redirect('/admin/productos')
    
    # Obtener datos del producto para editar
    producto = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        conn.close()
    
    if not producto:
        return "Producto no encontrado", 404
    
    categorias = Categorias.obtener_todas()
    return render_template('admin/editar_producto.html', producto=producto, categorias=categorias)

# Eliminar producto
@app.route('/admin/productos/eliminar/<int:producto_id>')
@admin_required
def admin_eliminar_producto(producto_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM productos WHERE id = %s', (producto_id,))
        conn.commit()
        conn.close()
    
    return redirect('/admin/productos')



# Cambiar rol de usuario
@app.route('/admin/usuarios/cambiar_rol/<int:user_id>')
@admin_required
def admin_cambiar_rol(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Obtener rol actual
        cursor.execute('SELECT rol FROM usuarios WHERE id = %s', (user_id,))
        usuario = cursor.fetchone()
        
        if usuario:
            nuevo_rol = 'admin' if usuario['rol'] == 'cliente' else 'cliente'
            cursor.execute('UPDATE usuarios SET rol = %s WHERE id = %s', (nuevo_rol, user_id))
            conn.commit()
        
        conn.close()
    
    return redirect('/admin/usuarios')

# Activar/Desactivar usuario
@app.route('/admin/usuarios/toggle_activo/<int:user_id>')
@admin_required
def admin_toggle_activo(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Obtener estado actual
        cursor.execute('SELECT activo FROM usuarios WHERE id = %s', (user_id,))
        usuario = cursor.fetchone()
        
        if usuario:
            nuevo_estado = not usuario['activo']
            cursor.execute('UPDATE usuarios SET activo = %s WHERE id = %s', (nuevo_estado, user_id))
            conn.commit()
        
        conn.close()
    
    return redirect('/admin/usuarios')


# =============================================
# RUTAS DE PERFIL DE USUARIO
# =============================================

# Perfil de usuario
@app.route('/perfil')
@login_required
def perfil():
    user = Auth.get_user_by_id(session['user_id'])
    addresses = Auth.get_user_addresses(session['user_id'])
    return render_template('perfil.html', user=user, addresses=addresses)

# Editar perfil
@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        
        success, message = Auth.update_user_profile(session['user_id'], nombre, apellido, telefono)
        
        if success:
            # Actualizar sesión
            session['user_nombre'] = nombre
            return redirect('/perfil')
        else:
            user = Auth.get_user_by_id(session['user_id'])
            return render_template('editar_perfil.html', user=user, error=message)
    
    user = Auth.get_user_by_id(session['user_id'])
    return render_template('editar_perfil.html', user=user)

# Cambiar contraseña
@app.route('/perfil/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            return render_template('cambiar_password.html', error="Las contraseñas no coinciden")
        
        if len(new_password) < 6:
            return render_template('cambiar_password.html', error="La contraseña debe tener al menos 6 caracteres")
        
        success, message = Auth.change_password(session['user_id'], current_password, new_password)
        
        if success:
            return render_template('cambiar_password.html', success=message)
        else:
            return render_template('cambiar_password.html', error=message)
    
    return render_template('cambiar_password.html')

# Gestión de direcciones
@app.route('/perfil/direcciones')
@login_required
def direcciones():
    user = Auth.get_user_by_id(session['user_id'])
    addresses = Auth.get_user_addresses(session['user_id'])
    return render_template('direcciones.html', user=user, addresses=addresses)

# Agregar dirección
@app.route('/perfil/direcciones/nueva', methods=['GET', 'POST'])
@login_required
def nueva_direccion():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        ciudad = request.form['ciudad']
        codigo_postal = request.form['codigo_postal']
        telefono_contacto = request.form['telefono_contacto']
        es_principal = 'es_principal' in request.form
        
        success, message = Auth.add_user_address(
            session['user_id'], nombre, direccion, ciudad, 
            codigo_postal, telefono_contacto, es_principal
        )
        
        if success:
            return redirect('/perfil/direcciones')
        else:
            return render_template('nueva_direccion.html', error=message)
    
    return render_template('nueva_direccion.html')

# Eliminar dirección
@app.route('/perfil/direcciones/eliminar/<int:address_id>')
@login_required
def eliminar_direccion(address_id):
    success, message = Auth.delete_user_address(address_id, session['user_id'])
    return redirect('/perfil/direcciones')

# Establecer dirección principal
@app.route('/perfil/direcciones/principal/<int:address_id>')
@login_required
def direccion_principal(address_id):
    success, message = Auth.set_primary_address(address_id, session['user_id'])
    return redirect('/perfil/direcciones')


# =============================================
# RUTAS DE CARRITO PERSISTENTE
# =============================================

@app.route('/api/carrito/agregar/<int:producto_id>')
@login_required
def api_agregar_carrito_db(producto_id):
    """API para agregar producto al carrito en BD"""
    success, message = CarritoDB.agregar_al_carrito(session['user_id'], producto_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400

@app.route('/api/carrito/actualizar/<int:producto_id>/<int:cantidad>')
@login_required
def api_actualizar_carrito_db(producto_id, cantidad):
    """API para actualizar cantidad en carrito BD"""
    success, message = CarritoDB.actualizar_cantidad(session['user_id'], producto_id, cantidad)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400

@app.route('/api/carrito/eliminar/<int:producto_id>')
@login_required
def api_eliminar_carrito_db(producto_id):
    """API para eliminar producto del carrito BD"""
    success, message = CarritoDB.eliminar_del_carrito(session['user_id'], producto_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400

@app.route('/api/carrito/contador')
@login_required
def api_contador_carrito_db():
    """API para obtener contador del carrito desde BD"""
    contador = CarritoDB.obtener_contador_carrito(session['user_id'])
    return jsonify({'contador': contador})

# =============================================
# RUTAS DE PEDIDOS
# =============================================

@app.route('/checkout')
@login_required
def checkout():
    """Página de checkout SIN DESCUENTOS"""
    carrito = CarritoDB.obtener_carrito_usuario(session['user_id'])
    direcciones = Auth.get_user_addresses(session['user_id'])
    
    if not carrito:
        return redirect('/carrito')
    
    # Calcular totales SIN DESCUENTOS
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)
    envio = 0 if subtotal > 200 else 15
    total = subtotal + envio  # SIN DESCUENTO
    
    return render_template('checkout.html', 
                         carrito=carrito, 
                         direcciones=direcciones,
                         subtotal=subtotal,
                         envio=envio,
                         total=total)

@app.route('/procesar-pedido', methods=['POST'])
@login_required
def procesar_pedido():
    """Procesar pedido SIN DESCUENTOS"""
    direccion_id = request.form.get('direccion_id')
    metodo_pago = request.form.get('metodo_pago')
    
    # Obtener dirección seleccionada
    direcciones = Auth.get_user_addresses(session['user_id'])
    direccion_seleccionada = next((d for d in direcciones if d['id'] == int(direccion_id)), None)
    
    if not direccion_seleccionada:
        return "Dirección no válida", 400
    
    # Formatear dirección para el pedido
    direccion_texto = f"{direccion_seleccionada['nombre']}\n{direccion_seleccionada['direccion']}\n{direccion_seleccionada['ciudad']}\nCP: {direccion_seleccionada['codigo_postal']}"
    
    # Calcular totales SIN DESCUENTOS
    carrito = CarritoDB.obtener_carrito_usuario(session['user_id'])
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)
    envio = 0 if subtotal > 200 else 15
    total = subtotal + envio  # SIN DESCUENTO
    
    # Crear pedido SIN DESCUENTO
    success, numero_pedido, message = Pedidos.crear_pedido(
        session['user_id'], direccion_texto, metodo_pago, subtotal, envio, 0, total  # descuento = 0
    )
    
    if success:
        return redirect(f'/pedido-confirmado/{numero_pedido}')
    else:
        return render_template('checkout.html', 
                             carrito=carrito, 
                             direcciones=Auth.get_user_addresses(session['user_id']),
                             subtotal=subtotal,
                             envio=envio,
                             total=total,
                             error=message)

@app.route('/pedido-confirmado/<numero_pedido>')
@login_required
def pedido_confirmado(numero_pedido):
    """Página de confirmación de pedido"""
    return render_template('pedido_confirmado.html', numero_pedido=numero_pedido)

@app.route('/mis-pedidos')
@login_required
def mis_pedidos():
    """Página de historial de pedidos del usuario"""
    pedidos = Pedidos.obtener_pedidos_usuario(session['user_id'])
    return render_template('mis_pedidos.html', pedidos=pedidos)

@app.route('/pedido/<int:pedido_id>')
@login_required
def detalle_pedido(pedido_id):
    """Detalle de un pedido específico"""
    pedido = Pedidos.obtener_detalle_pedido(pedido_id, session['user_id'])
    if not pedido:
        return "Pedido no encontrado", 404
    
    # Crear una copia segura del pedido - ACTUALIZA LA CLAVE
    pedido_data = {
        'id': pedido['id'],
        'numero_pedido': pedido['numero_pedido'],
        'estado': pedido['estado'],
        'subtotal': pedido['subtotal'],
        'envio': pedido['envio'],
        'descuento': pedido['descuento'],
        'total': pedido['total'],
        'direccion_envio': pedido['direccion_envio'],
        'metodo_pago': pedido['metodo_pago'],
        'created_at': pedido['created_at'],
        'updated_at': pedido['updated_at'],
        'productos': pedido.get('productos', [])
    }
    
    return render_template('detalle_pedido.html', pedido=pedido_data)

@app.route('/producto/<int:producto_id>')
def detalle_producto(producto_id):
    """Página de detalle individual de producto"""
    conn = get_db_connection()
    producto = None
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()
        conn.close()
    
    if not producto:
        return "Producto no encontrado", 404
    
    # Obtener productos relacionados (misma categoría)
    conn = get_db_connection()
    productos_relacionados = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM productos 
            WHERE categoria = %s AND id != %s 
            LIMIT 4
        ''', (producto['categoria'], producto_id))
        productos_relacionados = cursor.fetchall()
        conn.close()
    
    return render_template('detalle_producto.html', 
                         producto=producto, 
                         productos_relacionados=productos_relacionados)

# =============================================
# RUTAS DE ADMIN PARA PEDIDOS
# =============================================

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    """Panel de administración de pedidos"""
    pedidos = Pedidos.obtener_todos_pedidos()
    return render_template('admin/pedidos.html', pedidos=pedidos)

@app.route('/admin/pedidos/<int:pedido_id>')
@admin_required
def admin_detalle_pedido(pedido_id):
    """Detalle de pedido para admin"""
    pedido = Pedidos.obtener_detalle_pedido(pedido_id)
    if not pedido:
        return "Pedido no encontrado", 404
    return render_template('admin/detalle_pedido.html', pedido=pedido)

@app.route('/admin/pedidos/actualizar-estado/<int:pedido_id>/<nuevo_estado>')
@admin_required
def admin_actualizar_estado_pedido(pedido_id, nuevo_estado):
    """Actualizar estado de pedido"""
    success, message = Pedidos.actualizar_estado_pedido(pedido_id, nuevo_estado)
    if success:
        return redirect(f'/admin/pedidos/{pedido_id}')
    else:
        return f"Error: {message}", 400
    

@app.route('/admin/categorias')
@admin_required
def admin_categorias():
    """Gestión de categorías"""
    categorias = Categorias.obtener_todas()
    return render_template('admin/categorias.html', categorias=categorias)

@app.route('/admin/categorias/agregar', methods=['POST'])
@admin_required
def admin_agregar_categoria():
    """Agregar nueva categoría desde el modal"""
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion', '')
    
    if not nombre:
        return jsonify({'success': False, 'error': 'El nombre de la categoría es requerido'})
    
    success, message = Categorias.agregar(nombre, descripcion)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/api/categorias')
@admin_required
def api_categorias():
    """API para obtener todas las categorías"""
    categorias = Categorias.obtener_todas()
    return jsonify(categorias)

@app.route('/admin/categorias/eliminar/<int:categoria_id>')
@admin_required
def admin_eliminar_categoria(categoria_id):
    """Eliminar categoría"""
    success, message = Categorias.eliminar(categoria_id)
    return redirect('/admin/categorias')


@app.route('/api/carrito/detalle')
@login_required
def api_detalle_carrito_db():
    """API para obtener detalle del carrito desde BD"""
    carrito = CarritoDB.obtener_carrito_usuario(session['user_id'])
    return jsonify(carrito)
    

# =============================================
# INICIALIZACIÓN
# =============================================

# Crear carpeta de uploads si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    print(f"✅ Carpeta creada: {app.config['UPLOAD_FOLDER']}")

if __name__ == "__main__":
    # Iniciar sistema de keep-alive
    start_keep_alive()
    
    # Detectar si se está ejecutando en Render o localmente
    en_render = os.environ.get("RENDER", "False") == "True"

    # Configurar el puerto
    port = int(os.environ.get("PORT", 5000))

    # Determinar modo debug
    debug_mode = not en_render

    # Mensaje informativo
    if en_render:
        print("🌐 Iniciando aplicación Flask en Render (modo producción)")
        print("🔧 Keep-alive system: ACTIVADO")
    else:
        print("🟢 Iniciando aplicación Flask en modo local (debug activado)")
        print("🔧 Keep-alive system: DESACTIVADO (modo local)")

    # Ejecutar la app
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

