from servicios.servicio_entradas import validar_placa


def registrar_salida(parqueadero):
    print("\n--- REGISTRAR SALIDA ---")

    try:
        placa = validar_placa(input("Ingrese la placa del vehículo: "))
        numero_espacio, vehiculo = parqueadero.registrar_salida(placa)
        hora_salida = parqueadero.hora_actual()
        cobro = parqueadero.calcular_tiempo_y_tarifa(
            vehiculo.hora_entrada,
            hora_salida,
            vehiculo.tipo
        )

        parqueadero.historial_salidas.append({
            "espacio": numero_espacio,
            "placa": vehiculo.placa,
            "tipo": vehiculo.tipo,
            "hora_entrada": vehiculo.hora_entrada,
            "hora_salida": hora_salida,
            "tiempo_estadia": cobro["tiempo_estadia"],
            "horas_cobradas": cobro["horas_cobradas"],
            "total_pagar": cobro["total_pagar"],
        })
        parqueadero.guardar_en_json()

        print(f"Salida registrada correctamente. Espacio liberado: {numero_espacio}")
        print(f"{vehiculo.mostrar_informacion()} | Salida: {hora_salida}")
        print(f"Tiempo de estadía: {cobro['tiempo_estadia']} ({cobro['horas_cobradas']} hora(s) cobrada(s))")
        print(f"Tarifa por hora ({vehiculo.tipo.capitalize()}): ${cobro['tarifa_hora']:,}")
        print(f"TOTAL A PAGAR: ${cobro['total_pagar']:,}")

    except ValueError as error:
        print(f"No se pudo registrar la salida: {error}")

    input("\nPresione Enter para volver al menú...")
