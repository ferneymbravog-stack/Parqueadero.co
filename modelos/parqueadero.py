import json
import math
import os
from datetime import datetime   # el datetime es para manejar hora y fecha en el parqueadero 
from modelos.espacio import Espacio # esto es inportante para saber si los espacios estan libres o no 
from modelos.vehiculo import Vehiculo
from config import TARIFAS_POR_HORA, ARCHIVO_DATOS_JSON


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

    def guardar_en_json(self, ruta_archivo=ARCHIVO_DATOS_JSON):
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

    def cargar_desde_json(self, ruta_archivo=ARCHIVO_DATOS_JSON):
        if not os.path.exists(ruta_archivo):
            return False

        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        for espacio in self.espacios:
            espacio.vehiculo = None

        for item in datos.get("espacios_ocupados", []):
            numero = item["numero"]
            if 1 <= numero <= len(self.espacios):
                vehiculo = Vehiculo(
                    placa=item["placa"],
                    tipo=item["tipo"],
                    hora_entrada=item["hora_entrada"],
                )
                self.espacios[numero - 1].ocupar(vehiculo)

        self.historial_salidas = datos.get("historial_salidas", [])
        return True
#aca es donde nos devuelve la hora y la fecha 
    @staticmethod
    def hora_actual():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
