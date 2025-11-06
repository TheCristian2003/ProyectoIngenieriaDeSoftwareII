-- Crear base de datos
CREATE DATABASE IF NOT EXISTS tienda_tecnologia;
USE tienda_tecnologia;

-- Crear tabla productos
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

-- Crear tabla usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

USE tienda_tecnologia;

-- Insertar productos de ejemplo
INSERT INTO productos (nombre, descripcion, precio, categoria, stock, imagen) VALUES
('Procesador Intel Core i7-12700K', 'Procesador de 12 núcleos, 4.9GHz Turbo', 350.00, 'Procesadores', 15, 'cpu_intel.jpg'),
('Tarjeta Gráfica NVIDIA RTX 4060', '8GB GDDR6, Ray Tracing, DLSS 3', 450.00, 'Tarjetas Gráficas', 8, 'gpu_nvidia.jpg'),
('Memoria RAM Corsair 16GB DDR4', '3200MHz, CL16, 2x8GB Kit', 80.00, 'Memoria RAM', 25, 'ram_corsair.jpg'),
('SSD Samsung 1TB NVMe M.2', 'Velocidad lectura 3500MB/s, PCIe 3.0', 120.00, 'Almacenamiento', 20, 'ssd_samsung.jpg'),
('Placa Base ASUS B660', 'Socket LGA1700, DDR4, PCIe 4.0', 180.00, 'Placas Base', 12, 'motherboard_asus.jpg'),
('Fuente Alimentación 750W 80+ Gold', 'Full modular, certificación 80 Plus Gold', 110.00, 'Fuentes Alimentación', 10, 'psu_gold.jpg'),
('Monitor Gaming 24" 144Hz', '1080p, 1ms, FreeSync, HDMI/DisplayPort', 220.00, 'Monitores', 6, 'monitor_gaming.jpg'),
('Teclado Mecánico RGB', 'Switches Red, Retroiluminación RGB', 75.00, 'Periféricos', 18, 'teclado_mecanico.jpg');

UPDATE productos SET imagen = 'procesadores/ProcesadorIntelCorei7-12700K.png' WHERE id = 1;
UPDATE productos SET imagen = 'tarjetas_graficas/TarjetaGraficaNVIDIARTX4060.png' WHERE id = 2;
UPDATE productos SET imagen = 'rams/MemoriaRAMCorsair16GBDDR4.png' WHERE id = 3;
UPDATE productos SET imagen = 'discos_duros/SSDSamsung1TBNVMeM2.png' WHERE id = 4;
UPDATE productos SET imagen = 'placas_base/PlacaBaseASUSB660.png' WHERE id = 5;
UPDATE productos SET imagen = 'fuentes/FuenteAlimentacion750W80Gold.png' WHERE id = 6;
UPDATE productos SET imagen = 'monitores/MonitorGaming24pulgadas144Hz.png' WHERE id = 7;
UPDATE productos SET imagen = 'teclados/TecladoMecanicoRGB.png' WHERE id = 8;

SELECT id, nombre, imagen FROM productos;