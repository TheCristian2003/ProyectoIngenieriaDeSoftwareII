// Carrito en localStorage
let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

// Actualizar contador del carrito
function actualizarContadorCarrito() {
    const contador = document.getElementById('contador-carrito');
    if (contador) {
        contador.textContent = carrito.reduce((total, item) => total + item.cantidad, 0);
    }
}

// Agregar producto al carrito
async function agregarAlCarrito(productoId) {
    try {
        // Obtener información del producto desde la API
        const response = await fetch(`/api/productos/${productoId}`);
        const producto = await response.json();
        
        // Verificar si el producto ya está en el carrito
        const itemExistente = carrito.find(item => item.id === productoId);
        
        if (itemExistente) {
            itemExistente.cantidad += 1;
        } else {
            carrito.push({
                id: producto.id,
                nombre: producto.nombre,
                precio: producto.precio,
                imagen: producto.imagen,
                categoria: producto.categoria,
                cantidad: 1
            });
        }
        
        localStorage.setItem('carrito', JSON.stringify(carrito));
        actualizarContadorCarrito();
        
        // Mostrar notificación
        mostrarNotificacion('✅ Producto agregado al carrito!');
        
    } catch (error) {
        console.error('Error al agregar producto:', error);
        mostrarNotificacion('❌ Error al agregar producto');
    }
}

// Mostrar notificación
function mostrarNotificacion(mensaje) {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = 'alert alert-success position-fixed';
    notificacion.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 250px;';
    notificacion.textContent = mensaje;
    
    document.body.appendChild(notificacion);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notificacion.remove();
    }, 3000);
}

// Cargar y mostrar el carrito
function cargarCarrito() {
    const listaCarrito = document.getElementById('lista-carrito');
    const carritoVacio = document.getElementById('carrito-vacio');
    
    if (carrito.length === 0) {
        if (listaCarrito) listaCarrito.innerHTML = '';
        if (carritoVacio) carritoVacio.style.display = 'block';
        actualizarResumen();
        return;
    }
    
    if (carritoVacio) carritoVacio.style.display = 'none';
    
    // Generar HTML para los productos del carrito
    let html = '';
    carrito.forEach((item, index) => {
        html += `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-2">
                            <div class="image-container" style="height: 80px; padding: 5px;">
                                <img src="/static/images/productos/${item.imagen}" 
                                    class="product-image" 
                                    alt="${item.nombre}"
                                    onerror="this.src='https://via.placeholder.com/70x50/ffffff/007bff?text=P${item.id}'">
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h6 class="mb-1">${item.nombre}</h6>
                            <small class="text-muted">${item.categoria}</small>
                        </div>
                        <div class="col-md-2">
                            <span class="price">$${item.precio}</span>
                        </div>
                        <div class="col-md-2">
                            <div class="input-group input-group-sm">
                                <button class="btn btn-outline-secondary" onclick="cambiarCantidad(${index}, -1)">-</button>
                                <input type="number" class="form-control text-center" value="${item.cantidad}" min="1" 
                                       onchange="actualizarCantidad(${index}, this.value)">
                                <button class="btn btn-outline-secondary" onclick="cambiarCantidad(${index}, 1)">+</button>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <strong>$${(item.precio * item.cantidad).toFixed(2)}</strong>
                        </div>
                        <div class="col-md-1">
                            <button class="btn btn-danger btn-sm" onclick="eliminarDelCarrito(${index})">
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
    
    actualizarResumen();
}

// Funciones para manipular el carrito
function cambiarCantidad(index, cambio) {
    const nuevaCantidad = carrito[index].cantidad + cambio;
    if (nuevaCantidad >= 1) {
        carrito[index].cantidad = nuevaCantidad;
        guardarYActualizarCarrito();
    }
}

function actualizarCantidad(index, nuevaCantidad) {
    nuevaCantidad = parseInt(nuevaCantidad);
    if (nuevaCantidad >= 1) {
        carrito[index].cantidad = nuevaCantidad;
        guardarYActualizarCarrito();
    }
}

function eliminarDelCarrito(index) {
    if (confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
        carrito.splice(index, 1);
        guardarYActualizarCarrito();
    }
}

function vaciarCarrito() {
    if (confirm('¿Estás seguro de que quieres vaciar todo el carrito?')) {
        carrito = [];
        guardarYActualizarCarrito();
    }
}

function guardarYActualizarCarrito() {
    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarContadorCarrito();
    cargarCarrito();
}

// Actualizar resumen de compra
function actualizarResumen() {
    const subtotal = carrito.reduce((total, item) => total + (item.precio * item.cantidad), 0);
    const envio = subtotal > 200 ? 0 : 15;
    const descuento = 0;
    const total = subtotal + envio - descuento;
    
    if (document.getElementById('subtotal')) {
        document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('envio').textContent = `$${envio.toFixed(2)}`;
        document.getElementById('descuento').textContent = `-$${descuento.toFixed(2)}`;
        document.getElementById('total').textContent = `$${total.toFixed(2)}`;
    }
}

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