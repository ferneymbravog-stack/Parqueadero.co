from modelos.parqueadero import Parqueadero  #esto es para importara la clase parqueadero 
from servicios.servicio_entradas import registrar_entrada  #esta importa la funcion que solicita los datos de vehiculos y registra la entreade de ellos 
from config import CAPACIDAD_PARQUEADERO  #este es el que importa la constante que indica cuantos espacios tiene el parqueadero 


def mostrar_menu():
    print("\n===== SISTEMA DE CONTROL DE PARQUEADERO =====")
    print("  =======||=======")
    print(r"    _ /_____\ _  ")
    print(r"  //           \\ ")
    print(" || [::]  [::] || ")
    print(" |======GT======| ")
    print(r" /_O__________O_\ ")
    print("1. Registrar entrada de vehículo")
    print("2. Consultar vehículos estacionados")
    print("3. Consultar espacios disponibles")
    print("4. Salir")

#def es la palabra reservada que permite definir una funcion 
def main():
    parqueadero = Parqueadero(CAPACIDAD_PARQUEADERO)

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_entrada(parqueadero)
        elif opcion == "2":
            parqueadero.mostrar_vehiculos()
        elif opcion == "3":
            parqueadero.mostrar_disponibilidad()
        elif opcion == "4":
            print("Gracias por utilizar el sistema. ¡Hasta pronto!")
            break
        else:
            print("Opción inválida. Seleccione una opción del 1 al 4.")


if __name__ == "__main__":
    main()
