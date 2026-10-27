# Configuración inicial del sistema es de una capacidad de 10 espacios esta se puede modificar si se necesitan mas. 
CAPACIDAD_PARQUEADERO = 10
TIPOS_VEHICULO_VALIDOS = ("carro", "motocicleta")

# Tarifas por hora o fracción según el tipo de vehículo
TARIFAS_POR_HORA = {
    "carro": 3000,
    "motocicleta": 1500,
}

# Ruta del archivo JSON para persistencia de datos
ARCHIVO_DATOS_JSON = "datos/parqueadero.json"

# Rutas por defecto para la exportación de archivos CSV
ARCHIVO_REGISTROS_CSV = "datos/registros_parqueadero.csv"
ARCHIVO_REPORTE_CSV = "datos/reporte_ocupacion_ingresos.csv"
