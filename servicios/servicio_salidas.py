from servicios.servicio_entradas import validar_placa


def registrar_salida(parqueadero):
    print("\n--- REGISTRAR SALIDA ---")

    try:
        placa = validar_placa(input("Ingrese la placa del vehículo: "))
        espacio = parqueadero.buscar_vehiculo(placa)
        if espacio is None:
            raise ValueError("No se encontró ningún vehículo estacionado con esa placa.")

        hora_salida = parqueadero.hora_actual()
        # Primero validamos y calculamos la tarifa antes de liberar el espacio
        parqueadero.calcular_tiempo_y_tarifa(
            espacio.vehiculo.hora_entrada,
            hora_salida,
            espacio.vehiculo.tipo
        )

        numero_espacio, vehiculo = parqueadero.registrar_salida(placa)
        cobro = parqueadero.registrar_historial_salida(
            numero_espacio,
            vehiculo,
            hora_salida
        )
        parqueadero.guardar_en_json()

        print(f"Salida registrada correctamente. Espacio liberado: {numero_espacio}")
        print(f"{vehiculo.mostrar_informacion()} | Salida: {hora_salida}")
        print(f"Tiempo de estadía: {cobro['tiempo_estadia']} ({cobro['horas_cobradas']} hora(s) cobrada(s))")
        print(f"Tarifa por hora ({vehiculo.tipo.capitalize()}): ${cobro['tarifa_hora']:,}")
        print(f"TOTAL A PAGAR: ${cobro['total_pagar']:,}")

    except ValueError as error:
        print(f"No se pudo registrar la salida: {error}")

    input("\nPresione Enter para volver al menú...")
