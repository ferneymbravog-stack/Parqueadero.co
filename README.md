# Sistema de Control de Parqueadero

Aplicación de consola en Python para administrar entradas y salidas de vehículos, asignar y liberar espacios, calcular tarifas por tiempo y tipo de vehículo, realizar consultas y persistir la información en JSON.

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

## Funcionalidades
- Menú interactivo de consola.
- Registro de entradas y asignación automática de espacios.
- Registro de salidas, liberación de espacios y cálculo de tarifas por hora o fracción.
- Submenú de consultas (por placa, vehículos estacionados y disponibilidad de espacios).
- Guardado y recuperación automática de datos en `datos/parqueadero.json`.
