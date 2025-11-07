from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from database import get_db_connection
from auth import Auth
import os

app = Flask(__name__)
app.secret_key = 'techstore_secret_key_2024'  # Clave para las sesiones

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

# Ruta de perfil de usuario
@app.route('/perfil')
@login_required
def perfil():
    user = Auth.get_user_by_id(session['user_id'])
    return render_template('perfil.html', user=user)

# Ruta de administración (solo para admins)
@app.route('/admin')
@admin_required
def admin_panel():
    users = Auth.get_all_users()
    return render_template('admin.html', users=users)





if __name__ == '__main__':
    app.run(debug=True)