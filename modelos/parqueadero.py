from datetime import datetime   # el datetime es para manejar hora y fecha en el parqueadero 
from modelos.espacio import Espacio # esto es inportante para saber si los espacios estan libres o no 


class Parqueadero:
    """Administra los espacios y los vehículos estacionados."""
#_init_ es un método especial que se ejecuta cuando creamos un objeto de la clase , self representa en objeto actual 
    def __init__(self, capacidad):
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un entero positivo.")
      #esto crea automatcamente los espacios y los guarda en una lista 
        self.espacios = [Espacio(numero) for numero in range(1, capacidad + 1)]

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
        print("\n--- DISPONIBILIDAD DEL PARQUEADERO ---")
        print(f"Capacidad total: {len(self.espacios)}")
        print(f"Espacios ocupados: {ocupados}")
        print(f"Espacios disponibles: {self.cantidad_disponible()}")
#aca es donde nos devuelve la hora y la fecha 
    @staticmethod
    def hora_actual():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
