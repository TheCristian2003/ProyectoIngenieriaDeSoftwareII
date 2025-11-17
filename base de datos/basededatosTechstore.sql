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

CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




-- Insertar admin con el hash CORRECTO
INSERT INTO usuarios (email, password, nombre, apellido, rol) 
VALUES ('admin@techstore.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrador', 'Principal', 'admin');

INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Procesador Intel Core i7-12700K', 'Procesador de 12 núcleos, 4.9GHz Turbo', 350.00, 'Procesadores', 15, 'cpu_intel.jpg'),
('Tarjeta Gráfica NVIDIA RTX 4060', '8GB GDDR6, Ray Tracing, DLSS 3', 450.00, 'Tarjetas Gráficas', 8, 'gpu_nvidia.jpg'),
('Memoria RAM Corsair 16GB DDR4', '3200MHz, CL16, 2x8GB Kit', 80.00, 'Memoria RAM', 25, 'ram_corsair.jpg'),
('SSD Samsung 1TB NVMe M.2', 'Velocidad lectura 3500MB/s, PCIe 3.0', 120.00, 'Almacenamiento', 20, 'ssd_samsung.jpg'),
('Placa Base ASUS B660', 'Socket LGA1700, DDR4, PCIe 4.0', 180.00, 'Placas Base', 12, 'motherboard_asus.jpg'),
('Fuente Alimentación 750W 80+ Gold', 'Full modular, certificación 80 Plus Gold', 110.00, 'Fuentes Alimentación', 10, 'psu_gold.jpg'),
('Monitor Gaming 24" 144Hz', '1080p, 1ms, FreeSync, HDMI/DisplayPort', 220.00, 'Monitores', 6, 'monitor_gaming.jpg'),
('Teclado Mecánico RGB', 'Switches Red, Retroiluminación RGB', 75.00, 'Periféricos', 18, 'teclado_mecanico.jpg');

-- Procesadores
INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Procesador Intel Core i9-13900K', '24 núcleos, 32 hilos, 5.8GHz Turbo', 650.00, 'Procesadores', 8, 'procesadores/intel_i9_13900k.jpg'),
('Procesador AMD Ryzen 9 7950X', '16 núcleos, 32 hilos, 5.7GHz Boost', 650.00, 'Procesadores', 6, 'procesadores/amd_ryzen9_7950x.jpg'),
('Procesador Intel Core i5-13600K', '14 núcleos, 20 hilos, 5.1GHz Turbo', 320.00, 'Procesadores', 12, 'procesadores/intel_i5_13600k.jpg');

-- Tarjetas Gráficas
INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('NVIDIA RTX 4090 24GB', '24GB GDDR6X, DLSS 3, Ray Tracing', 1600.00, 'Tarjetas Gráficas', 3, 'tarjetas_graficas/nvidia_rtx4090.jpg'),
('AMD Radeon RX 7900 XTX', '24GB GDDR6, Ray Accelerators', 1000.00, 'Tarjetas Gráficas', 5, 'tarjetas_graficas/amd_rx7900xtx.jpg'),
('NVIDIA RTX 4070 Ti 12GB', '12GB GDDR6X, DLSS 3, 4K Gaming', 800.00, 'Tarjetas Gráficas', 7, 'tarjetas_graficas/nvidia_rtx4070ti.jpg');

-- Memoria RAM
INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Corsair Vengeance RGB 32GB DDR5', '5600MHz, CL36, RGB Sync', 150.00, 'Memoria RAM', 15, 'memoria_ram/corsair_ddr5_rgb.jpg'),
('G.Skill Trident Z5 64GB DDR5', '6000MHz, CL30, 2x32GB Kit', 280.00, 'Memoria RAM', 4, 'memoria_ram/gskill_trident_ddr5.jpg'),
('Kingston Fury Beast 16GB DDR4', '3200MHz, CL16, Plug & Play', 55.00, 'Memoria RAM', 20, 'memoria_ram/kingston_fury_ddr4.jpg');

-- Almacenamiento
INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Samsung 990 Pro 2TB NVMe', '7450MB/s lectura, PCIe 4.0', 180.00, 'Almacenamiento', 10, 'almacenamiento/samsung_990pro.jpg'),
('WD Blue SN570 1TB NVMe', '3500MB/s lectura, PCIe 3.0', 65.00, 'Almacenamiento', 18, 'almacenamiento/wd_blue_sn570.jpg'),
('Seagate Barracuda 4TB HDD', '5400RPM, SATA III, 256MB cache', 85.00, 'Almacenamiento', 12, 'almacenamiento/seagate_barracuda.jpg');

-- Refrigeración
INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Cooler Master Hyper 212', 'Torre simple, 120mm, 4 pipas calor', 45.00, 'Refrigeración', 15, 'refrigeracion/coolermaster_hyper212.jpg'),
('NZXT Kraken X73', 'AIO 360mm, RGB, LCD display', 180.00, 'Refrigeración', 6, 'refrigeracion/nzxt_kraken_x73.jpg'),
('Arctic Freezer 34 eSports', 'Doble ventilador, 4 pipas calor', 40.00, 'Refrigeración', 12, 'refrigeracion/arctic_freezer34.jpg');

-- Gabinetes
INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Lian Li O11 Dynamic', 'Mid Tower, Cristal templado, RGB', 150.00, 'Torres', 8, 'gabinetes/lianli_o11.jpg'),
('Corsair 4000D Airflow', 'Mid Tower, Mesh front panel, USB-C', 95.00, 'Torres', 10, 'gabinetes/corsair_4000d.jpg'),
('Fractal Design Meshify 2', 'Mid Tower, Panel mesh, Modular', 130.00, 'Torres', 6, 'gabinetes/fractal_meshify2.jpg');




INSERT INTO categorias (nombre, descripcion) VALUES 
('Procesadores', 'Unidades de procesamiento central (CPU)'),
('Tarjetas Gráficas', 'Tarjetas de video y aceleradores gráficos'),
('Memoria RAM', 'Memoria de acceso aleatorio'),
('Almacenamiento', 'Discos duros, SSDs y unidades de almacenamiento'),
('Placas Base', 'Motherboards y placas base'),
('Fuentes Alimentación', 'Fuentes de poder y alimentación'),
('Monitores', 'Pantallas y monitores'),
('Periféricos', 'Teclados, mouse y accesorios'),
('Refrigeración', 'Sistemas de refrigeración para PC');


UPDATE productos SET categoria = 'Procesadores' WHERE categoria LIKE '%Procesador%';
UPDATE productos SET categoria = 'Tarjetas Gráficas' WHERE categoria LIKE '%Tarjeta%';
UPDATE productos SET categoria = 'Memoria RAM' WHERE categoria LIKE '%Memoria%';
UPDATE productos SET categoria = 'Almacenamiento' WHERE categoria LIKE '%Almacenamiento%';
UPDATE productos SET categoria = 'Placas Base' WHERE categoria LIKE '%Placa%';
UPDATE productos SET categoria = 'Fuentes Alimentación' WHERE categoria LIKE '%Fuente%';
UPDATE productos SET categoria = 'Monitores' WHERE categoria LIKE '%Monitor%';
UPDATE productos SET categoria = 'Periféricos' WHERE categoria LIKE '%Periféricos%';


SELECT * FROM categorias;
SELECT id, nombre, categoria FROM productos;
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