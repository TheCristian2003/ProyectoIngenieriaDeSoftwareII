CREATE DATABASE IF NOT EXISTS tienda_tecnologia;
USE tienda_tecnologia;

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50),
    stock INT DEFAULT 0,
    imagen VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    telefono VARCHAR(20),
    rol ENUM('cliente', 'admin') DEFAULT 'cliente',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP NULL
);


CREATE TABLE IF NOT EXISTS direcciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    codigo_postal VARCHAR(20),
    telefono_contacto VARCHAR(20),
    es_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS carritos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    UNIQUE KEY unique_carrito_item (usuario_id, producto_id)
);


CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    numero_pedido VARCHAR(20) UNIQUE NOT NULL,
    estado ENUM('pendiente', 'confirmado', 'en_proceso', 'enviado', 'entregado', 'cancelado') DEFAULT 'pendiente',
    subtotal DECIMAL(10,2) NOT NULL,
    envio DECIMAL(10,2) NOT NULL DEFAULT 0,
    descuento DECIMAL(10,2) NOT NULL DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    direccion_envio TEXT,
    metodo_pago VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla para items de pedidos
CREATE TABLE IF NOT EXISTS pedido_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);


DELETE FROM usuarios where id>0;

-- Insertar admin con el hash CORRECTO
INSERT INTO usuarios (email, password, nombre, apellido, rol) 
VALUES ('admin@techstore.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrador', 'Principal', 'admin');

SELECT id, email, password, nombre, rol FROM usuarios;

INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Procesador Intel Core i7-12700K', 'Procesador de 12 núcleos, 4.9GHz Turbo', 350.00, 'Procesadores', 15, 'cpu_intel.jpg'),
('Tarjeta Gráfica NVIDIA RTX 4060', '8GB GDDR6, Ray Tracing, DLSS 3', 450.00, 'Tarjetas Gráficas', 8, 'gpu_nvidia.jpg'),
('Memoria RAM Corsair 16GB DDR4', '3200MHz, CL16, 2x8GB Kit', 80.00, 'Memoria RAM', 25, 'ram_corsair.jpg'),
('SSD Samsung 1TB NVMe M.2', 'Velocidad lectura 3500MB/s, PCIe 3.0', 120.00, 'Almacenamiento', 20, 'ssd_samsung.jpg'),
('Placa Base ASUS B660', 'Socket LGA1700, DDR4, PCIe 4.0', 180.00, 'Placas Base', 12, 'motherboard_asus.jpg'),
('Fuente Alimentación 750W 80+ Gold', 'Full modular, certificación 80 Plus Gold', 110.00, 'Fuentes Alimentación', 10, 'psu_gold.jpg'),
('Monitor Gaming 24" 144Hz', '1080p, 1ms, FreeSync, HDMI/DisplayPort', 220.00, 'Monitores', 6, 'monitor_gaming.jpg'),
('Teclado Mecánico RGB', 'Switches Red, Retroiluminación RGB', 75.00, 'Periféricos', 18, 'teclado_mecanico.jpg');

INSERT INTO direcciones (usuario_id, nombre, direccion, ciudad, codigo_postal, telefono_contacto, es_principal) 
VALUES (5, 'Casa Principal', 'Calle Falsa 123', 'Bogotá', '110011', '3001234567', TRUE);


UPDATE productos SET imagen = 'procesadores/ProcesadorIntelCorei7-12700K.png' WHERE id = 1;
UPDATE productos SET imagen = 'tarjetas_graficas/TarjetaGraficaNVIDIARTX4060.png' WHERE id = 2;
UPDATE productos SET imagen = 'rams/MemoriaRAMCorsair16GBDDR4.png' WHERE id = 3;
UPDATE productos SET imagen = 'discos_duros/SSDSamsung1TBNVMeM2.png' WHERE id = 4;
UPDATE productos SET imagen = 'placas_base/PlacaBaseASUSB660.png' WHERE id = 5;
UPDATE productos SET imagen = 'fuentes/FuenteAlimentacion750W80Gold.png' WHERE id = 6;
UPDATE productos SET imagen = 'monitores/MonitorGaming24pulgadas144Hz.png' WHERE id = 7;
UPDATE productos SET imagen = 'teclados/TecladoMecanicoRGB.png' WHERE id = 8;

SELECT id, nombre, imagen, stock FROM productos;
select * from usuarios;
SELECT * FROM pedidos;
SELECT * FROM pedido_items;



-- Función para generar número de pedido único
DELIMITER //
CREATE FUNCTION generar_numero_pedido() RETURNS VARCHAR(20) READS SQL DATA
BEGIN
    DECLARE nuevo_numero VARCHAR(20);
    DECLARE contador INT;
    
    SET contador = (SELECT COUNT(*) + 1 FROM pedidos WHERE DATE(created_at) = CURDATE());
    SET nuevo_numero = CONCAT('PED', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(contador, 4, '0'));
    
    RETURN nuevo_numero;
END//
DELIMITER ;