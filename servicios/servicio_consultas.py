from servicios.servicio_entradas import validar_placa


def consultar_por_placa(parqueadero):
    try:
        print("===== CONSULTA DE VEHÍCULO POR PLACA =====")
        placa = validar_placa(input("Ingrese la placa: "))
        espacio = parqueadero.buscar_vehiculo(placa)
        if espacio is not None:
            print(f"El vehículo con placa {placa} está estacionado en el espacio {espacio.numero}.")
            print(espacio.vehiculo.mostrar_informacion())
        else:
            print(f"No se encontró ningún vehículo con la placa {placa}.")
    except ValueError as error:
        print(error)

    input("\nPresione Enter para continuar...")


def consultar_estacionados(parqueadero):
    parqueadero.mostrar_vehiculos()
    input("\nPresione Enter para continuar...")


def menu_consultas(parqueadero):
    while True:
        print("\n--- MENÚ DE CONSULTAS ---")
        print("1. Consultar por placa")
        print("2. Ver vehículos estacionados")
        print("3. Consultar espacios disponibles")
        print("4. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            consultar_por_placa(parqueadero)
        elif opcion == "2":
            consultar_estacionados(parqueadero)
        elif opcion == "3":
            parqueadero.mostrar_disponibilidad()
            input("\nPresione Enter para continuar...")
        elif opcion == "4":
            break
        else:
            print("Opción inválida. Seleccione una opción del 1 al 4.")
