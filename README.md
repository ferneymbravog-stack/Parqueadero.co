# Sistema de Control de Parqueadero

Aplicación de consola en Python para registrar entradas de vehículos, asignar espacios y consultar ocupación.

## Requisitos
- Python 3.10 o superior (no usa librerías externas).

## Ejecutar
Desde la carpeta raíz del proyecto:

```bash
python main.py
```

## Ejecutar pruebas
```bash
python -m unittest discover -s pruebas -v
```

## Funcionalidades iniciales
- Menú de consola.
- Registro de entradas.
- Asignación automática de espacios.
- Validación básica de placas y tipo de vehículo.
- Consulta de vehículos estacionados.
- Consulta de disponibilidad.

## Alcance de esta versión
Esta versión es el incremento inicial para las tareas T-01 a T-04. La salida de vehículos, las tarifas, la persistencia JSON y la exportación CSV se desarrollarán en los siguientes incrementos.
