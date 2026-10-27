from modelos.parqueadero import Parqueadero  #esto es para importara la clase parqueadero 
from servicios.servicio_entradas import registrar_entrada  #esta importa la funcion que solicita los datos de vehiculos y registra la entreade de ellos 
from servicios.servicio_salidas import registrar_salida
from servicios.servicio_consultas import menu_consultas, generar_informe, exportar_csv
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
    print("2. Registrar salida de vehículo")
    print("3. Consultas (por placa / vehículos estacionados)")
    print("4. Consultar espacios disponibles")
    print("5. Generar informe de ocupación e ingresos")
    print("6. Exportar registros y reportes a CSV")
    print("7. Salir")

#def es la palabra reservada que permite definir una funcion 
def main():
    parqueadero = Parqueadero(CAPACIDAD_PARQUEADERO)
    parqueadero.cargar_desde_json()

    try:
        while True:
            mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                registrar_entrada(parqueadero)
            elif opcion == "2":
                registrar_salida(parqueadero)
            elif opcion == "3":
                menu_consultas(parqueadero)
            elif opcion == "4":
                parqueadero.mostrar_disponibilidad()
                input("\nPresione Enter para volver al menú...")
            elif opcion == "5":
                generar_informe(parqueadero)
            elif opcion == "6":
                exportar_csv(parqueadero)
            elif opcion == "7":
                print("Gracias por utilizar el sistema. ¡Hasta pronto!")
                break
            else:
                print("Opción inválida. Seleccione una opción del 1 al 7.")
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo del sistema de forma segura. ¡Hasta pronto!")


if __name__ == "__main__":
    main()
