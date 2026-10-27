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


def generar_informe(parqueadero):
    print("\n--- INFORMES DE OCUPACIÓN E INGRESOS ---")
    print("1. Ver informe general completo (ocupación actual e ingresos totales)")
    print("2. Filtrar ingresos e historial de salidas por fecha (ej. día de hoy)")
    subopcion = input("Seleccione una opción (1-2, Enter para general): ").strip()

    if subopcion in ("", "1"):
        parqueadero.mostrar_informe_ocupacion_e_ingresos()
    elif subopcion == "2":
        consultar_ingresos_por_fecha(parqueadero, pausar=False)
    else:
        print("Opción inválida. Seleccione 1 o 2.")

    input("\nPresione Enter para continuar...")


def consultar_ingresos_por_fecha(parqueadero, pausar=True):
    fecha = input("Ingrese la fecha a consultar (AAAA-MM-DD) o escriba 'hoy': ").strip()
    if not fecha:
        fecha = "hoy"
    try:
        parqueadero.mostrar_informe_por_fecha(fecha)
    except ValueError as error:
        print(f"No se pudo generar el informe por fecha: {error}")

    if pausar:
        input("\nPresione Enter para continuar...")


def menu_consultas(parqueadero):
    while True:
        print("\n--- MENÚ DE CONSULTAS E INFORMES ---")
        print("1. Consultar por placa")
        print("2. Ver vehículos estacionados")
        print("3. Consultar espacios disponibles")
        print("4. Generar informe de ocupación e ingresos")
        print("5. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            consultar_por_placa(parqueadero)
        elif opcion == "2":
            consultar_estacionados(parqueadero)
        elif opcion == "3":
            parqueadero.mostrar_disponibilidad()
            input("\nPresione Enter para continuar...")
        elif opcion == "4":
            generar_informe(parqueadero)
        elif opcion == "5":
            break
        else:
            print("Opción inválida. Seleccione una opción del 1 al 5.")
