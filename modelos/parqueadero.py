import csv
import json
import math
import os
from datetime import datetime   # el datetime es para manejar hora y fecha en el parqueadero 
from modelos.espacio import Espacio # esto es inportante para saber si los espacios estan libres o no 
from modelos.vehiculo import Vehiculo
from config import (
    TARIFAS_POR_HORA,
    ARCHIVO_DATOS_JSON,
    ARCHIVO_REGISTROS_CSV,
    ARCHIVO_REPORTE_CSV,
)


class Parqueadero:
    """Administra los espacios y los vehículos estacionados."""
#_init_ es un método especial que se ejecuta cuando creamos un objeto de la clase , self representa en objeto actual 
    def __init__(self, capacidad):
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un entero positivo.")
      #esto crea automatcamente los espacios y los guarda en una lista 
        self.espacios = [Espacio(numero) for numero in range(1, capacidad + 1)]
        self.historial_salidas = []

    def buscar_vehiculo(self, placa):
        placa = placa.strip().upper()
        for espacio in self.espacios:
            if not espacio.esta_libre and espacio.vehiculo.placa == placa:
                return espacio
        return None
#primero buscamos si ya esta la placa en el parquedaro si ya esta registra y el carro esta dentro esto se hace para impedir que se dupliquen , segundo se busca si hay espacio libre next() en un solo recurido optiene un resultado es decir si hay espacio y si no hay espacio next devuelve el valor none si no encuentra un espacio libre.
    def registrar_entrada(self, vehiculo):
        if self.buscar_vehiculo(vehiculo.placa):
            raise ValueError("Ya hay un vehículo estacionado con esa placa.")

        espacio_libre = next(
            (espacio for espacio in self.espacios if espacio.esta_libre),
            None
        )

        if espacio_libre is None:
            raise ValueError("El parqueadero está lleno. No hay espacios disponibles.")
#aca se muestra que espacio del parqueadero esta libre es decir si el espacio 3 esta libre lo muestra para que otro auto lo utilize 
        espacio_libre.ocupar(vehiculo)
        return espacio_libre.numero

    def registrar_salida(self, placa):
        espacio = self.buscar_vehiculo(placa)
        if espacio is None:
            raise ValueError("No se encontró ningún vehículo estacionado con esa placa.")

        vehiculo = espacio.vehiculo
        numero_espacio = espacio.numero
        espacio.liberar()
        return numero_espacio, vehiculo

    def calcular_tiempo_y_tarifa(self, hora_entrada, hora_salida, tipo):
        formato = "%Y-%m-%d %H:%M:%S"
        inicio = datetime.strptime(hora_entrada, formato)
        fin = datetime.strptime(hora_salida, formato)

        if fin < inicio:
            raise ValueError("La hora de salida no puede ser anterior a la de entrada.")

        tipo = tipo.strip().lower()
        if tipo == "moto":
            tipo = "motocicleta"

        if tipo not in TARIFAS_POR_HORA:
            raise ValueError("Tipo de vehículo inválido para calcular la tarifa.")

        segundos_totales = int((fin - inicio).total_seconds())
        horas_cobradas = max(1, math.ceil(segundos_totales / 3600))
        tarifa_unitaria = TARIFAS_POR_HORA[tipo]
        total_pagar = horas_cobradas * tarifa_unitaria

        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60
        tiempo_formateado = f"{horas}h {minutos}m {segundos}s"

        return {
            "tiempo_estadia": tiempo_formateado,
            "horas_cobradas": horas_cobradas,
            "tarifa_hora": tarifa_unitaria,
            "total_pagar": total_pagar,
        }

    def calcular_tarifa(self, hora_entrada, hora_salida, tipo):
        resultado = self.calcular_tiempo_y_tarifa(hora_entrada, hora_salida, tipo)
        return resultado["total_pagar"]

# aca se crea y devuelve una lista con los vehículos que están estacionados , porque se utiliza return porque evuelve la lista, pero no la imprime. Por eso se utiliza return y no print sirve mejor asi.
    def obtener_vehiculos(self):
        return [
            espacio.vehiculo
            for espacio in self.espacios
            if not espacio.esta_libre
        ]
#aca se cuentan cuantos espacios hay disponibles para el uso 
    def cantidad_disponible(self):
        return sum(1 for espacio in self.espacios if espacio.esta_libre)
#aca se utiliza la lista que ya tenemos de los espacios y los autos que ya estan , despues de ver los espacios muestra la informacion de los carros que se encuentran dentro del parqueadero 

    def mostrar_vehiculos(self):
        vehiculos = self.obtener_vehiculos()
        if not vehiculos:
            print("No hay vehículos estacionados.")
            return

        print("\n--- VEHÍCULOS ESTACIONADOS ---")
        for espacio in self.espacios:
            if not espacio.esta_libre:
                print(
                    f"Espacio {espacio.numero}: "
                    f"{espacio.vehiculo.mostrar_informacion()}"
                )
#aca se muestra la disponibilidad o un resumen de como se encuentra el parqueadero en ese momento 
    def mostrar_disponibilidad(self):
        ocupados = len(self.espacios) - self.cantidad_disponible()
        libres = [str(espacio.numero) for espacio in self.espacios if espacio.esta_libre]
        print("\n--- DISPONIBILIDAD DEL PARQUEADERO ---")
        print(f"Capacidad total: {len(self.espacios)}")
        print(f"Espacios ocupados: {ocupados}")
        print(f"Espacios disponibles: {self.cantidad_disponible()}")
        print(f"Números de espacio libres: {', '.join(libres) if libres else 'Ninguno'}")

    def registrar_historial_salida(self, numero_espacio, vehiculo, hora_salida):
        cobro = self.calcular_tiempo_y_tarifa(
            vehiculo.hora_entrada,
            hora_salida,
            vehiculo.tipo
        )
        registro = {
            "espacio": numero_espacio,
            "placa": vehiculo.placa,
            "tipo": vehiculo.tipo,
            "hora_entrada": vehiculo.hora_entrada,
            "hora_salida": hora_salida,
            "tiempo_estadia": cobro["tiempo_estadia"],
            "horas_cobradas": cobro["horas_cobradas"],
            "total_pagar": cobro["total_pagar"],
        }
        self.historial_salidas.append(registro)
        return cobro

    def obtener_informe_ocupacion(self):
        capacidad_total = len(self.espacios)
        disponibles = self.cantidad_disponible()
        ocupados = capacidad_total - disponibles
        porcentaje_ocupacion = round((ocupados / capacidad_total) * 100, 2) if capacidad_total > 0 else 0.0

        ocupacion_por_tipo = {tipo: 0 for tipo in TARIFAS_POR_HORA}
        for vehiculo in self.obtener_vehiculos():
            tipo = "motocicleta" if vehiculo.tipo == "moto" else vehiculo.tipo
            ocupacion_por_tipo[tipo] = ocupacion_por_tipo.get(tipo, 0) + 1

        return {
            "capacidad_total": capacidad_total,
            "espacios_ocupados": ocupados,
            "espacios_disponibles": disponibles,
            "porcentaje_ocupacion": porcentaje_ocupacion,
            "ocupacion_por_tipo": ocupacion_por_tipo,
        }

    def obtener_informe_ingresos(self, fecha=None):
        if fecha is not None:
            fecha = fecha.strip().lower()
            if fecha == "hoy":
                fecha = datetime.now().strftime("%Y-%m-%d")
            else:
                try:
                    datetime.strptime(fecha, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Formato de fecha inválido. Use el formato AAAA-MM-DD (ej. 2026-10-25) o 'hoy'.")

            salidas_evaluadas = [
                salida for salida in self.historial_salidas
                if str(salida.get("hora_salida", "")).startswith(fecha)
            ]
        else:
            salidas_evaluadas = list(self.historial_salidas)

        ingresos_totales = 0
        horas_totales = 0
        ingresos_por_tipo = {tipo: 0 for tipo in TARIFAS_POR_HORA}
        salidas_por_tipo = {tipo: 0 for tipo in TARIFAS_POR_HORA}

        for salida in salidas_evaluadas:
            pago = salida.get("total_pagar", 0)
            horas = salida.get("horas_cobradas", 0)
            tipo = salida.get("tipo", "").strip().lower()
            if tipo == "moto":
                tipo = "motocicleta"

            ingresos_totales += pago
            horas_totales += horas
            ingresos_por_tipo[tipo] = ingresos_por_tipo.get(tipo, 0) + pago
            salidas_por_tipo[tipo] = salidas_por_tipo.get(tipo, 0) + 1

        return {
            "fecha_filtro": fecha,
            "total_salidas": len(salidas_evaluadas),
            "horas_totales_cobradas": horas_totales,
            "ingresos_totales": ingresos_totales,
            "ingresos_por_tipo": ingresos_por_tipo,
            "salidas_por_tipo": salidas_por_tipo,
            "historial_filtrado": salidas_evaluadas,
        }

    def mostrar_informe_por_fecha(self, fecha):
        ingresos = self.obtener_informe_ingresos(fecha=fecha)
        fecha_mostrada = ingresos["fecha_filtro"]

        print("\n==============================================")
        print(f"   INFORME DE INGRESOS POR FECHA ({fecha_mostrada})")
        print("==============================================")
        print(f"Total de vehículos atendidos (salidas): {ingresos['total_salidas']}")
        print(f"Total de horas cobradas:                {ingresos['horas_totales_cobradas']} hora(s)")
        print(f"INGRESOS RECAUDADOS EN LA FECHA:        ${ingresos['ingresos_totales']:,}")
        print("Desglose por tipo de vehículo:")
        for tipo, monto in ingresos["ingresos_por_tipo"].items():
            cantidad_salidas = ingresos["salidas_por_tipo"].get(tipo, 0)
            print(f"  - {tipo.capitalize()} ({cantidad_salidas} salida(s)): ${monto:,}")

        historial_fecha = ingresos["historial_filtrado"]
        if historial_fecha:
            print(f"\n--- HISTORIAL DE SALIDAS DEL {fecha_mostrada} ---")
            for idx, item in enumerate(historial_fecha, start=1):
                print(
                    f"{idx}. Placa: {item.get('placa')} | "
                    f"Tipo: {str(item.get('tipo', '')).capitalize()} | "
                    f"Espacio: {item.get('espacio')} | "
                    f"Salida: {item.get('hora_salida')} | "
                    f"Estadía: {item.get('tiempo_estadia')} | "
                    f"Pagado: ${item.get('total_pagar', 0):,}"
                )
        else:
            print(f"\nNo se registraron salidas en la fecha {fecha_mostrada}.")

    def mostrar_informe_ocupacion_e_ingresos(self):
        ocupacion = self.obtener_informe_ocupacion()
        ingresos = self.obtener_informe_ingresos()

        print("\n==============================================")
        print("   INFORME DE OCUPACIÓN E INGRESOS")
        print("==============================================")
        print("\n--- 1. ESTADO DE OCUPACIÓN ACTUAL ---")
        print(f"Capacidad total:       {ocupacion['capacidad_total']} espacios")
        print(f"Espacios ocupados:     {ocupacion['espacios_ocupados']}")
        print(f"Espacios disponibles:  {ocupacion['espacios_disponibles']}")
        print(f"Porcentaje ocupación:  {ocupacion['porcentaje_ocupacion']}%")
        print("Vehículos estacionados por tipo:")
        for tipo, cantidad in ocupacion["ocupacion_por_tipo"].items():
            print(f"  - {tipo.capitalize()}: {cantidad}")

        print("\n--- 2. RESUMEN DE INGRESOS Y SALIDAS ---")
        print(f"Total de vehículos atendidos (salidas): {ingresos['total_salidas']}")
        print(f"Total de horas cobradas:                {ingresos['horas_totales_cobradas']} hora(s)")
        print(f"INGRESOS TOTALES RECAUDADOS:            ${ingresos['ingresos_totales']:,}")
        print("Desglose de ingresos por tipo de vehículo:")
        for tipo, monto in ingresos["ingresos_por_tipo"].items():
            cantidad_salidas = ingresos["salidas_por_tipo"].get(tipo, 0)
            print(f"  - {tipo.capitalize()} ({cantidad_salidas} salida(s)): ${monto:,}")

        if self.historial_salidas:
            print("\n--- 3. HISTORIAL DE SALIDAS REGISTRADAS ---")
            for idx, item in enumerate(self.historial_salidas, start=1):
                print(
                    f"{idx}. Placa: {item.get('placa')} | "
                    f"Tipo: {str(item.get('tipo', '')).capitalize()} | "
                    f"Espacio: {item.get('espacio')} | "
                    f"Estadía: {item.get('tiempo_estadia')} | "
                    f"Pagado: ${item.get('total_pagar', 0):,}"
                )
        else:
            print("\nNo se han registrado salidas facturadas hasta el momento.")

    def exportar_registros_csv(self, ruta_archivo=ARCHIVO_REGISTROS_CSV):
        """Exporta los vehículos estacionados actualmente y el historial de salidas a un archivo CSV."""
        try:
            carpeta = os.path.dirname(ruta_archivo)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)

            encabezados = [
                "estado",
                "espacio",
                "placa",
                "tipo",
                "hora_entrada",
                "hora_salida",
                "tiempo_estadia",
                "horas_cobradas",
                "total_pagar",
            ]

            with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
                escritor = csv.DictWriter(archivo_csv, fieldnames=encabezados)
                escritor.writeheader()

                for espacio in self.espacios:
                    if not espacio.esta_libre:
                        escritor.writerow({
                            "estado": "Estacionado",
                            "espacio": espacio.numero,
                            "placa": espacio.vehiculo.placa,
                            "tipo": espacio.vehiculo.tipo,
                            "hora_entrada": espacio.vehiculo.hora_entrada,
                            "hora_salida": "En curso",
                            "tiempo_estadia": "En curso",
                            "horas_cobradas": 0,
                            "total_pagar": 0,
                        })

                for salida in self.historial_salidas:
                    escritor.writerow({
                        "estado": "Finalizado",
                        "espacio": salida.get("espacio", ""),
                        "placa": salida.get("placa", ""),
                        "tipo": salida.get("tipo", ""),
                        "hora_entrada": salida.get("hora_entrada", ""),
                        "hora_salida": salida.get("hora_salida", ""),
                        "tiempo_estadia": salida.get("tiempo_estadia", ""),
                        "horas_cobradas": salida.get("horas_cobradas", 0),
                        "total_pagar": salida.get("total_pagar", 0),
                    })

            return True
        except OSError as error:
            print(f"Error al exportar registros a CSV en '{ruta_archivo}': {error}")
            return False

    def exportar_reporte_csv(self, ruta_archivo=ARCHIVO_REPORTE_CSV):
        """Exporta el resumen estadístico de ocupación e ingresos a un archivo CSV."""
        try:
            carpeta = os.path.dirname(ruta_archivo)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)

            ocupacion = self.obtener_informe_ocupacion()
            ingresos = self.obtener_informe_ingresos()

            filas = [
                {"categoria": "Ocupacion", "indicador": "Capacidad total", "valor": ocupacion["capacidad_total"]},
                {"categoria": "Ocupacion", "indicador": "Espacios ocupados", "valor": ocupacion["espacios_ocupados"]},
                {"categoria": "Ocupacion", "indicador": "Espacios disponibles", "valor": ocupacion["espacios_disponibles"]},
                {"categoria": "Ocupacion", "indicador": "Porcentaje de ocupacion (%)", "valor": ocupacion["porcentaje_ocupacion"]},
            ]

            for tipo, cantidad in ocupacion["ocupacion_por_tipo"].items():
                filas.append({
                    "categoria": "Ocupacion por tipo",
                    "indicador": f"Vehiculos estacionados ({tipo})",
                    "valor": cantidad,
                })

            filas.extend([
                {"categoria": "Ingresos", "indicador": "Total salidas atendidas", "valor": ingresos["total_salidas"]},
                {"categoria": "Ingresos", "indicador": "Total horas cobradas", "valor": ingresos["horas_totales_cobradas"]},
                {"categoria": "Ingresos", "indicador": "Ingresos totales recaudados", "valor": ingresos["ingresos_totales"]},
            ])

            for tipo, monto in ingresos["ingresos_por_tipo"].items():
                salidas_tipo = ingresos["salidas_por_tipo"].get(tipo, 0)
                filas.append({
                    "categoria": "Ingresos por tipo",
                    "indicador": f"Salidas registradas ({tipo})",
                    "valor": salidas_tipo,
                })
                filas.append({
                    "categoria": "Ingresos por tipo",
                    "indicador": f"Total recaudado ({tipo})",
                    "valor": monto,
                })

            with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
                escritor = csv.DictWriter(archivo_csv, fieldnames=["categoria", "indicador", "valor"])
                escritor.writeheader()
                escritor.writerows(filas)

            return True
        except OSError as error:
            print(f"Error al exportar reporte a CSV en '{ruta_archivo}': {error}")
            return False

    def exportar_todo_csv(self, ruta_registros=ARCHIVO_REGISTROS_CSV, ruta_reporte=ARCHIVO_REPORTE_CSV):
        """Exporta tanto los registros detallados como el reporte de ocupación e ingresos."""
        ok_registros = self.exportar_registros_csv(ruta_registros)
        ok_reporte = self.exportar_reporte_csv(ruta_reporte)
        return ok_registros and ok_reporte

    def guardar_en_json(self, ruta_archivo=ARCHIVO_DATOS_JSON):
        try:
            carpeta = os.path.dirname(ruta_archivo)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)

            datos = {
                "capacidad": len(self.espacios),
                "espacios_ocupados": [
                    {
                        "numero": espacio.numero,
                        "placa": espacio.vehiculo.placa,
                        "tipo": espacio.vehiculo.tipo,
                        "hora_entrada": espacio.vehiculo.hora_entrada,
                    }
                    for espacio in self.espacios
                    if not espacio.esta_libre
                ],
                "historial_salidas": self.historial_salidas,
            }

            with open(ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            return True
        except OSError as error:
            print(f"Error al guardar los datos en '{ruta_archivo}': {error}")
            return False

    def _reiniciar_estado(self):
        for espacio in self.espacios:
            espacio.vehiculo = None
        self.historial_salidas = []

    def cargar_desde_json(self, ruta_archivo=ARCHIVO_DATOS_JSON):
        if not os.path.exists(ruta_archivo):
            print(f"Aviso: El archivo '{ruta_archivo}' no existe. Se inicializará uno nuevo.")
            self._reiniciar_estado()
            self.guardar_en_json(ruta_archivo)
            return False

        try:
            if os.path.getsize(ruta_archivo) == 0:
                raise ValueError("El archivo JSON está vacío.")

            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            if not isinstance(datos, dict):
                raise ValueError("El contenido raíz del JSON debe ser un objeto (diccionario).")

            espacios_ocupados = datos.get("espacios_ocupados", [])
            historial_salidas = datos.get("historial_salidas", [])

            if not isinstance(espacios_ocupados, list) or not isinstance(historial_salidas, list):
                raise ValueError("'espacios_ocupados' e 'historial_salidas' deben ser listas.")

            self._reiniciar_estado()

            for item in espacios_ocupados:
                if not isinstance(item, dict):
                    raise ValueError("Cada registro de espacio ocupado debe ser un objeto JSON.")

                campos_requeridos = ("numero", "placa", "tipo", "hora_entrada")
                if not all(campo in item for campo in campos_requeridos):
                    raise ValueError("Faltan campos obligatorios en un registro de vehículo.")

                numero = item["numero"]
                placa = item["placa"]
                tipo = item["tipo"]
                hora_entrada = item["hora_entrada"]

                if not isinstance(numero, int) or isinstance(numero, bool):
                    raise ValueError("El número de espacio debe ser un entero válido.")
                if not all(isinstance(val, str) and val.strip() for val in (placa, tipo, hora_entrada)):
                    raise ValueError("Los datos del vehículo (placa, tipo, hora_entrada) deben ser textos no vacíos.")

                if 1 <= numero <= len(self.espacios):
                    vehiculo = Vehiculo(
                        placa=placa,
                        tipo=tipo,
                        hora_entrada=hora_entrada,
                    )
                    self.espacios[numero - 1].ocupar(vehiculo)

            self.historial_salidas = historial_salidas
            return True

        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, KeyError, TypeError) as error:
            print(
                f"Advertencia: El archivo '{ruta_archivo}' está dañado o tiene datos inválidos ({error}). "
                "Se restablecerá el archivo con valores por defecto."
            )
            self._reiniciar_estado()
            self.guardar_en_json(ruta_archivo)
            return False
        except OSError as error:
            print(f"Error de lectura al abrir '{ruta_archivo}': {error}")
            self._reiniciar_estado()
            return False
#aca es donde nos devuelve la hora y la fecha 
    @staticmethod
    def hora_actual():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
