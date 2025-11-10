// Cargar carrito desde base de datos al iniciar
async function cargarCarritoDesdeBD() {
    if (!usuarioLogueado()) return;
    
    try {
        const response = await fetch('/api/carrito/contador');
        const data = await response.json();
        actualizarContadorCarrito(data.contador);
        
        // Si estamos en la página del carrito, cargar los productos
        if (window.location.pathname === '/carrito') {
            await cargarCarritoBD();
        }
    } catch (error) {
        console.error('Error al cargar carrito:', error);
    }
}

// Cargar y mostrar el carrito desde BD
async function cargarCarritoBD() {
    const listaCarrito = document.getElementById('lista-carrito');
    const carritoVacio = document.getElementById('carrito-vacio');
    
    if (!usuarioLogueado()) {
        mostrarCarritoNoLogueado();
        return;
    }

    try {
        const response = await fetch('/api/carrito/detalle');
        const carrito = await response.json();
        
        if (carrito.length === 0) {
            if (listaCarrito) listaCarrito.innerHTML = '';
            if (carritoVacio) carritoVacio.style.display = 'block';
            actualizarResumen({subtotal: 0, envio: 0, descuento: 0, total: 0});
            return;
        }
        
        if (carritoVacio) carritoVacio.style.display = 'none';
        
        // Generar HTML para los productos del carrito
        let html = '';
        let subtotal = 0;
        
        carrito.forEach((item) => {
            const itemSubtotal = item.precio * item.cantidad;
            subtotal += itemSubtotal;
            
            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-2">
                                <div class="image-container" style="height: 80px; padding: 5px;">
                                    <img src="/static/images/productos/${item.imagen}" 
                                         class="product-image" 
                                         alt="${item.nombre}"
                                         onerror="this.src='https://via.placeholder.com/70x50/ffffff/007bff?text=P${item.producto_id}'">
                                </div>
                            </div>
                            <div class="col-md-3">
                                <h6 class="mb-1">${item.nombre}</h6>
                                <small class="text-muted">${item.categoria}</small>
                            </div>
                            <div class="col-md-2">
                                <span class="price">$${item.precio}</span>
                            </div>
                            <div class="col-md-2">
                                <div class="input-group input-group-sm">
                                    <button class="btn btn-outline-secondary" onclick="cambiarCantidadBD(${item.producto_id}, -1)">-</button>
                                    <input type="number" class="form-control text-center" value="${item.cantidad}" min="1" 
                                           onchange="actualizarCantidadBD(${item.producto_id}, this.value)">
                                    <button class="btn btn-outline-secondary" onclick="cambiarCantidadBD(${item.producto_id}, 1)">+</button>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <strong>$${itemSubtotal.toFixed(2)}</strong>
                            </div>
                            <div class="col-md-1">
                                <button class="btn btn-danger btn-sm" onclick="eliminarDelCarritoBD(${item.producto_id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        if (listaCarrito) {
            listaCarrito.innerHTML = html;
        }
        
        const envio = subtotal > 200 ? 0 : 15;
        const descuento = 0;
        const total = subtotal + envio - descuento;
        
        actualizarResumen({subtotal, envio, descuento, total});
        
    } catch (error) {
        console.error('Error al cargar carrito:', error);
        mostrarNotificacion('❌ Error al cargar el carrito');
    }
}

// Funciones para manipular el carrito en BD
async function cambiarCantidadBD(productoId, cambio) {
    try {
        const response = await fetch(`/api/carrito/actualizar/${productoId}/${cambio}`);
        const data = await response.json();
        
        if (data.success) {
            await cargarCarritoBD();
            await actualizarContadorCarritoBD();
            mostrarNotificacion('✅ Carrito actualizado');
        } else {
            mostrarNotificacion('❌ ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('❌ Error al actualizar cantidad');
    }
}

async function actualizarCantidadBD(productoId, nuevaCantidad) {
    nuevaCantidad = parseInt(nuevaCantidad);
    if (nuevaCantidad >= 1) {
        await cambiarCantidadBD(productoId, nuevaCantidad - 1); // Ajustar para el cambio
    }
}

async function eliminarDelCarritoBD(productoId) {
    if (confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
        try {
            const response = await fetch(`/api/carrito/eliminar/${productoId}`);
            const data = await response.json();
            
            if (data.success) {
                await cargarCarritoBD();
                await actualizarContadorCarritoBD();
                mostrarNotificacion('✅ Producto eliminado');
            } else {
                mostrarNotificacion('❌ ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('❌ Error al eliminar producto');
        }
    }
}

async function vaciarCarritoBD() {
    if (confirm('¿Estás seguro de que quieres vaciar todo el carrito?')) {
        try {
            // Vaciar uno por uno (podríamos optimizar esto con una ruta específica)
            const response = await fetch('/api/carrito/detalle');
            const carrito = await response.json();
            
            for (const item of carrito) {
                await fetch(`/api/carrito/eliminar/${item.producto_id}`);
            }
            
            await cargarCarritoBD();
            await actualizarContadorCarritoBD();
            mostrarNotificacion('✅ Carrito vaciado');
        } catch (error) {
            console.error('Error:', error);
            mostrarNotificacion('❌ Error al vaciar carrito');
        }
    }
}

async function actualizarContadorCarritoBD() {
    if (!usuarioLogueado()) return;
    
    try {
        const response = await fetch('/api/carrito/contador');
        const data = await response.json();
        actualizarContadorCarrito(data.contador);
    } catch (error) {
        console.error('Error al actualizar contador:', error);
    }
}

// Agregar producto al carrito (versión BD)
async function agregarAlCarritoBD(productoId) {
    if (!usuarioLogueado()) {
        mostrarNotificacion('⚠️ Inicia sesión para agregar productos al carrito');
        return;
    }
    
    try {
        const response = await fetch(`/api/carrito/agregar/${productoId}`);
        const data = await response.json();
        
        if (data.success) {
            await actualizarContadorCarritoBD();
            mostrarNotificacion('✅ ' + data.message);
        } else {
            mostrarNotificacion('❌ ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('❌ Error al agregar producto');
    }
}

// Verificar si el usuario está logueado
function usuarioLogueado() {
    return typeof userLoggedIn !== 'undefined' && userLoggedIn;
}

// Mostrar mensaje cuando no está logueado
function mostrarCarritoNoLogueado() {
    const listaCarrito = document.getElementById('lista-carrito');
    const carritoVacio = document.getElementById('carrito-vacio');
    
    if (listaCarrito) {
        listaCarrito.innerHTML = `
            <div class="alert alert-warning text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Inicia sesión para ver tu carrito</strong><br>
                <a href="/login" class="btn btn-primary mt-2">Iniciar Sesión</a>
                <a href="/registro" class="btn btn-outline-primary mt-2">Registrarse</a>
            </div>
        `;
    }
    if (carritoVacio) carritoVacio.style.display = 'none';
    actualizarResumen({subtotal: 0, envio: 0, descuento: 0, total: 0});
}

// Mostrar notificación
function mostrarNotificacion(mensaje, tipo = 'success') {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `alert alert-${tipo} position-fixed`;
    notificacion.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 250px;';
    notificacion.textContent = mensaje;
    
    document.body.appendChild(notificacion);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notificacion.remove();
    }, 3000);
}

// Actualizar contador del carrito en el navbar
function actualizarContadorCarrito(contador) {
    const contadorElement = document.getElementById('contador-carrito');
    if (contadorElement) {
        contadorElement.textContent = contador;
    }
}


// Actualizar resumen de compra
function actualizarResumen(totales) {
    if (document.getElementById('subtotal')) {
        document.getElementById('subtotal').textContent = `$${totales.subtotal.toFixed(2)}`;
        document.getElementById('envio').textContent = `$${totales.envio.toFixed(2)}`;
        document.getElementById('descuento').textContent = `-$${totales.descuento.toFixed(2)}`;
        document.getElementById('total').textContent = `$${totales.total.toFixed(2)}`;
    }
}

// =============================================
// INICIALIZACIÓN
// =============================================

document.addEventListener('DOMContentLoaded', function() {
    // Determinar si el usuario está logueado
    window.userLoggedIn = document.body.classList.contains('user-logged-in');
    
    if (userLoggedIn) {
        cargarCarritoDesdeBD();
    } else {
        actualizarContadorCarrito(0);
    }
    
    // Para páginas específicas
    if (window.location.pathname === '/carrito') {
        if (userLoggedIn) {
            cargarCarritoBD();
        } else {
            mostrarCarritoNoLogueado();
        }
    }
});

// Aplicar descuento
function aplicarDescuento() {
    const codigo = document.getElementById('codigo-descuento').value;
    if (codigo === 'UNI2024') {
        mostrarNotificacion('🎉 ¡Descuento aplicado! 10% de descuento en tu compra.');
    } else {
        mostrarNotificacion('❌ Código inválido. Usa: UNI2024');
    }
}

// Simular compra
function simularCompra() {
    if (carrito.length === 0) {
        mostrarNotificacion('⚠️ Tu carrito está vacío');
        return;
    }
    
    const total = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    
    alert(`✅ ¡Compra simulada exitosamente!\n\nTotal de productos: ${carrito.reduce((sum, item) => sum + item.cantidad, 0)}\nTotal: $${total.toFixed(2)}\n\nGracias por probar TechStore.`);
    vaciarCarrito();
}

function procederPago() {
    simularCompra();
}

// Funciones para filtros y búsqueda (mantenemos las anteriores)
function filtrarProductos() {
    const categoria = document.getElementById('filtro-categoria').value;
    const precio = document.getElementById('filtro-precio').value;
    const buscar = document.getElementById('buscador').value.toLowerCase();
    
    const productos = document.querySelectorAll('.producto-item');
    let productosVisibles = 0;
    
    productos.forEach(producto => {
        const prodCategoria = producto.getAttribute('data-categoria');
        const prodPrecio = parseFloat(producto.getAttribute('data-precio'));
        const prodNombre = producto.getAttribute('data-nombre');
        
        let visible = true;
        
        if (categoria && prodCategoria !== categoria) visible = false;
        if (precio) {
            const [min, max] = precio.split('-').map(Number);
            if (max && (prodPrecio < min || prodPrecio > max)) visible = false;
            else if (!max && prodPrecio < min) visible = false;
        }
        if (buscar && !prodNombre.includes(buscar.toLowerCase())) visible = false;
        
        producto.style.display = visible ? 'block' : 'none';
        if (visible) productosVisibles++;
    });
    
    const sinResultados = document.getElementById('sin-resultados');
    if (sinResultados) {
        sinResultados.style.display = productosVisibles === 0 ? 'block' : 'none';
    }
}

function buscarProductos() { filtrarProductos(); }
function limpiarFiltros() {
    document.getElementById('filtro-categoria').value = '';
    document.getElementById('filtro-precio').value = '';
    document.getElementById('buscador').value = '';
    filtrarProductos();
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    actualizarContadorCarrito();
    if (window.location.pathname === '/carrito') cargarCarrito();
    if (window.location.pathname === '/productos') filtrarProductos();
});