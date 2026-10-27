from servicios.servicio_entradas import validar_placa
from config import ARCHIVO_REGISTROS_CSV, ARCHIVO_REPORTE_CSV


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


def exportar_csv(parqueadero):
    print("\n--- EXPORTAR REGISTROS Y REPORTES A CSV ---")
    print("1. Exportar registros de vehículos (estacionados e historial de salidas)")
    print("2. Exportar reporte estadístico de ocupación e ingresos")
    print("3. Exportar ambos archivos CSV")
    opcion = input("Seleccione una opción (1-3): ").strip()

    if opcion == "1":
        if parqueadero.exportar_registros_csv():
            print(f"Registros exportados exitosamente en: '{ARCHIVO_REGISTROS_CSV}'")
    elif opcion == "2":
        if parqueadero.exportar_reporte_csv():
            print(f"Reporte exportado exitosamente en: '{ARCHIVO_REPORTE_CSV}'")
    elif opcion == "3":
        if parqueadero.exportar_todo_csv():
            print(
                f"Archivos exportados exitosamente en:\n"
                f"  - '{ARCHIVO_REGISTROS_CSV}'\n"
                f"  - '{ARCHIVO_REPORTE_CSV}'"
            )
    else:
        print("Opción inválida. Seleccione una opción del 1 al 3.")

    input("\nPresione Enter para continuar...")


def menu_consultas(parqueadero):
    while True:
        print("\n--- MENÚ DE CONSULTAS E INFORMES ---")
        print("1. Consultar por placa")
        print("2. Ver vehículos estacionados")
        print("3. Consultar espacios disponibles")
        print("4. Generar informe de ocupación e ingresos")
        print("5. Exportar registros y reportes a CSV")
        print("6. Volver al menú principal")
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
            exportar_csv(parqueadero)
        elif opcion == "6":
            break
        else:
            print("Opción inválida. Seleccione una opción del 1 al 6.")
