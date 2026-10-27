# Sistema de Control de Parqueadero

Aplicación interactiva de consola desarrollada en Python para gestionar de principio a fin la operación de un parqueadero: registro de entradas y salidas de vehículos, asignación y liberación automática de espacios, cobro de tarifas por hora o fracción, generación de informes estadísticos de ocupación e ingresos, persistencia tolerante a fallos en formato JSON y exportación de datos a archivos CSV.

---

## Tabla de Contenidos
1. [Requisitos](#-requisitos)
2. [Estructura del Proyecto](#-estructura-del-proyecto)
3. [Cómo Ejecutar el Programa](#-cómo-ejecutar-el-programa)
4. [Cómo Funciona el Sistema (Menú y Opciones)](#-cómo-funciona-el-sistema-menú-y-opciones)
5. [Reglas de Negocio y Tarifas](#-reglas-de-negocio-y-tarifas)
6. [Persistencia en JSON y Manejo de Excepciones](#-persistencia-en-json-y-manejo-de-excepciones)
7. [Informes de Ocupación e Ingresos](#-informes-de-ocupación-e-ingresos)
8. [Exportación a Archivos CSV](#-exportación-a-archivos-csv)
9. [Pruebas Unitarias y Funcionales](#-pruebas-unitarias-y-funcionales)

---

## Requisitos
- **Python 3.10 o superior** (utiliza únicamente la librería estándar de Python: `json`, `csv`, `os`, `math`, `datetime`, `unittest`).

---

## Estructura del Proyecto

```text
sistema_parqueadero/
├── main.py                          # Punto de entrada y menú principal interactivo
├── config.py                        # Configuración global (capacidad, tarifas y rutas de archivos)
├── README.md                        # Documentación general del proyecto
├── datos/
│   ├── parqueadero.json             # Base de datos local en JSON (estado actual e historial)
│   ├── registros_parqueadero.csv    # Exportación CSV de vehículos estacionados y salidas
│   └── reporte_ocupacion_ingresos.csv # Exportación CSV de métricas de ocupación e ingresos
├── modelos/
│   ├── vehiculo.py                  # Clase Vehiculo (placa, tipo normalizado y hora de entrada)
│   ├── espacio.py                   # Clase Espacio (número de espacio, estado libre/ocupado)
│   └── parqueadero.py               # Clase Parqueadero (lógica central, tarifas, JSON y CSV)
├── servicios/
│   ├── servicio_entradas.py         # Validación de placas y flujo de registro de entradas
│   ├── servicio_salidas.py          # Flujo de salida, liquidación de tarifa y recibo en consola
│   └── servicio_consultas.py        # Submenú de consultas, informes y exportación a CSV
└── pruebas/
    └── test_parqueadero.py          # Suite de pruebas unitarias y funcionales (unittest)
```

---

## Cómo Ejecutar el Programa

Desde la carpeta raíz del proyecto, ejecuta en la terminal:

```bash
python main.py
```

Al iniciar, el sistema carga automáticamente los datos previos desde `datos/parqueadero.json`. Si el archivo no existe o presenta algún daño, se inicializa automáticamente sin interrumpir el arranque.

---

## Cómo Funciona el Sistema (Menú y Opciones)

El menú principal ofrece **7 opciones**:

1. **Registrar entrada de vehículo:**
   - Solicita la placa (entre 5 y 10 caracteres alfanuméricos, permite guion intermedio como `ABC-123`) y el tipo de vehículo (`carro`, `moto` o `motocicleta`).
   - Verifica que la placa no esté ya estacionada y asigna automáticamente el **primer espacio libre** disponible (del `1` al `10`).
   - Guarda inmediatamente el estado en `datos/parqueadero.json`.
2. **Registrar salida de vehículo:**
   - Busca el vehículo estacionado por su placa.
   - Calcula el tiempo exacto de estadía (`horas`, `minutos`, `segundos`) y las horas a cobrar (redondeando hacia arriba toda fracción de hora con `math.ceil` y cobrando mínimo 1 hora).
   - Libera el espacio, registra la transacción en el historial de salidas, actualiza el archivo JSON y muestra el recibo detallado con el **TOTAL A PAGAR**.
3. **Consultas e Informes (Submenú):**
   - **1. Consultar por placa:** Indica en qué número de espacio se encuentra un vehículo y su hora de ingreso.
   - **2. Ver vehículos estacionados:** Lista todos los vehículos actualmente dentro del parqueadero con su espacio asignado.
   - **3. Consultar espacios disponibles:** Muestra la capacidad total, cuántos espacios están ocupados/libres y la lista de números de espacio disponibles.
   - **4. Generar informe de ocupación e ingresos:** Muestra el reporte estadístico completo o filtrado por fecha.
   - **5. Exportar registros y reportes a CSV:** Permite generar los archivos `.csv`.
4. **Consultar espacios disponibles:** Acceso rápido al resumen de disponibilidad.
5. **Generar informe de ocupación e ingresos:** Acceso directo al reporte estadístico y financiero.
6. **Exportar registros y reportes a CSV:** Acceso directo al módulo de exportación CSV.
7. **Salir:** Cierra el programa de forma segura (también soporta salida limpia ante `Ctrl + C`).

---

## Reglas de Negocio y Tarifas

Configuradas en `config.py` (modificables según las necesidades del parqueadero):

| Parámetro | Valor por defecto | Descripción |
| :--- | :--- | :--- |
| `CAPACIDAD_PARQUEADERO` | `10` espacios | Cantidad máxima de vehículos simultáneos |
| Tarifa **Carro** | `$3,000` / hora o fracción | Cobro mínimo de 1 hora |
| Tarifa **Motocicleta** | `$1,500` / hora o fracción | Acepta `"moto"` o `"motocicleta"` |

---

## Persistencia en JSON y Manejo de Excepciones

El método `cargar_desde_json()` y `guardar_en_json()` en `modelos/parqueadero.py` protegen la integridad de los datos frente a errores comunes:
- **Archivo inexistente (`FileNotFoundError`):** Crea automáticamente la carpeta `datos/` y un archivo `parqueadero.json` inicial vacío.
- **Archivo vacío (`0 bytes`) o corrupto (`json.JSONDecodeError`):** Muestra una advertencia en consola, reinicia el estado en memoria de forma segura y reconstruye el archivo JSON con una estructura válida.
- **Validación estructural:** Comprueba que las listas `espacios_ocupados` e `historial_salidas` sean válidas, que no existan placas duplicadas, que las fechas cumplan el formato `%Y-%m-%d %H:%M:%S` y que los montos del historial sean numéricos.
- **Seguridad en salidas:** Antes de liberar un espacio en `registrar_salida`, se valida el cálculo de tiempo y tarifa para evitar perder el registro del vehículo si ocurre algún error de formato de fecha.

---

## Informes de Ocupación e Ingresos

Al seleccionar la opción **5** del menú principal (o **4** en el submenú de consultas), el usuario puede elegir entre dos tipos de reporte:
1. **Informe general completo:**
   - **Estado de ocupación actual:** Capacidad total, espacios ocupados, espacios disponibles, porcentaje de ocupación (`%`) y cantidad de vehículos estacionados por tipo (`Carro` vs. `Motocicleta`).
   - **Resumen de ingresos y salidas:** Total histórico de vehículos atendidos, horas facturadas, ingresos totales recaudados (`$`) y desglose por tipo de vehículo.
   - **Historial de salidas registradas:** Detalle cronológico de cada vehículo facturado.
2. **Filtro de ingresos e historial por fecha (ej. día de hoy):**
   - Permite ingresar una fecha en formato `AAAA-MM-DD` (por ejemplo, `2026-10-25`) o escribir `'hoy'` (o presionar `Enter`) para filtrar únicamente las salidas, horas cobradas y recaudación correspondientes a ese día específico.

---

## Exportación a Archivos CSV

### ¿Cómo se usa?
1. En el menú principal elige la **opción `6. Exportar registros y reportes a CSV`** (o desde `3. Consultas` -> `5`).
2. Selecciona una de las 3 modalidades:
   - **`1`**: Exportar únicamente los registros de vehículos (`datos/registros_parqueadero.csv`).
   - **`2`**: Exportar únicamente el reporte estadístico (`datos/reporte_ocupacion_ingresos.csv`).
   - **`3`**: Exportar ambos archivos CSV al mismo tiempo.

### Estructura de los archivos generados
1. **`datos/registros_parqueadero.csv`:**
   - Contiene tanto los vehículos que están actualmente dentro del parqueadero (`estado = Estacionado`) como los que ya salieron (`estado = Finalizado`).
   - **Columnas:** `estado,espacio,placa,tipo,hora_entrada,hora_salida,tiempo_estadia,horas_cobradas,total_pagar`
2. **`datos/reporte_ocupacion_ingresos.csv`:**
   - Resume todos los indicadores clave del negocio listos para abrir en Excel, Google Sheets o herramientas de análisis.
   - **Columnas:** `categoria,indicador,valor` (incluye métricas de `Ocupacion`, `Ocupacion por tipo`, `Ingresos` e `Ingresos por tipo`).

---

## Pruebas Unitarias y Funcionales

El proyecto cuenta con **17 pruebas automatizadas** en `pruebas/test_parqueadero.py` que validan:
- Asignación de espacios, bloqueo de placas duplicadas y límite de capacidad.
- Liberación de espacios y cobro por hora o fracción para carros y motocicletas.
- Guardado y recuperación en JSON, además de recuperación automática ante archivos JSON inexistentes, vacíos, corruptos o con estructura inválida.
- Cálculo de informes generales de ocupación e ingresos y **filtrado de ingresos por fecha (`AAAA-MM-DD` o `'hoy'`)**.
- Exportación y lectura verificada de los archivos CSV (`registros_parqueadero.csv` y `reporte_ocupacion_ingresos.csv`).
- Flujo funcional completo de extremo a extremo y simulación interactiva de entrada/consulta/salida por consola (`unittest.mock`).

Para ejecutar todas las pruebas:

```bash
python -m unittest discover -s pruebas -v
```
