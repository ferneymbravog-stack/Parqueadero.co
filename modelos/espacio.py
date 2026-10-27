class Espacio:
    """Representa un espacio físico del parqueadero."""
#esto es para crear el espacio y saber si hay un vehiculo dentro del espacio 
    def __init__(self, numero):
        self.numero = numero
        self.vehiculo = None
#esto @property nos permite consultar un método como si fuera un atributo 
    @property
    def esta_libre(self):
        return self.vehiculo is None
#esto hace que un vehiculo opcupe el espacio 
    def ocupar(self, vehiculo):
        if not self.esta_libre:
            raise ValueError(f"El espacio {self.numero} ya está ocupado.")
        self.vehiculo = vehiculo
#esto hace que se libere el espacio que esta ocupando un vehiculo 
    def liberar(self):
        if self.esta_libre:
            raise ValueError(f"El espacio {self.numero} ya está libre.")
        self.vehiculo = None
