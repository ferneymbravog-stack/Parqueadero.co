from modelos.vehiculo import Vehiculo
from config import TIPOS_VEHICULO_VALIDOS


def validar_placa(placa):
    placa = placa.strip().upper().replace(" ", "")
    # Validación básica: evita placas vacías o demasiado cortas.
    if len(placa) < 5 or len(placa) > 10:
        raise ValueError("La placa debe tener entre 5 y 10 caracteres.")
    if placa.startswith("-") or placa.endswith("-") or "--" in placa:
        raise ValueError("El guion en la placa solo puede ir en el medio (ej. ABC-123).")
    if not placa.replace("-", "").isalnum():
        raise ValueError("La placa solo puede contener letras, números y guion.")
    return placa


def registrar_entrada(parqueadero):
    print("\n--- REGISTRAR ENTRADA ---")

    try:
        placa = validar_placa(input("Ingrese la placa del vehículo: "))
        tipo = input("Tipo de vehículo (carro/moto): ").strip().lower()
        if tipo == "moto":
            tipo = "motocicleta"

        if tipo not in TIPOS_VEHICULO_VALIDOS:
            raise ValueError("Tipo inválido. Escriba 'carro', 'moto' o 'motocicleta'.")

        vehiculo = Vehiculo(
            placa=placa,
            tipo=tipo,
            hora_entrada=parqueadero.hora_actual()
        )

        numero_espacio = parqueadero.registrar_entrada(vehiculo)
        parqueadero.guardar_en_json()
        print(f"Entrada registrada correctamente. Espacio asignado: {numero_espacio}")

    except ValueError as error:
        print(f"No se pudo registrar la entrada: {error}")

    input("\nPresione Enter para volver al menú...")
