class Vehiculo:
    """Representa un vehículo registrado en el parqueadero."""

    def __init__(self, placa, tipo, hora_entrada):
        self.placa = placa.strip().upper()
        self.tipo = tipo.strip().lower()
        self.hora_entrada = hora_entrada

    def mostrar_informacion(self):
        return (
            f"Placa: {self.placa} | "
            f"Tipo: {self.tipo.capitalize()} | "
            f"Entrada: {self.hora_entrada}"
        )

