import unittest
from modelos.parqueadero import Parqueadero
from modelos.vehiculo import Vehiculo


class TestParqueadero(unittest.TestCase):
    def setUp(self):
        self.parqueadero = Parqueadero(2)

    def crear_vehiculo(self, placa):
        return Vehiculo(placa, "carro", "2026-10-21 09:00:00")

    def test_registra_vehiculo_y_asigna_espacio(self):
        numero = self.parqueadero.registrar_entrada(self.crear_vehiculo("ABC123"))
        self.assertEqual(numero, 1)

    def test_no_permite_placa_duplicada(self):
        self.parqueadero.registrar_entrada(self.crear_vehiculo("ABC123"))
        with self.assertRaises(ValueError):
            self.parqueadero.registrar_entrada(self.crear_vehiculo("ABC123"))

    def test_no_permite_superar_capacidad(self):
        self.parqueadero.registrar_entrada(self.crear_vehiculo("ABC123"))
        self.parqueadero.registrar_entrada(self.crear_vehiculo("XYZ789"))
        with self.assertRaises(ValueError):
            self.parqueadero.registrar_entrada(self.crear_vehiculo("JKL456"))

    def test_cuenta_espacios_disponibles(self):
        self.parqueadero.registrar_entrada(self.crear_vehiculo("ABC123"))
        self.assertEqual(self.parqueadero.cantidad_disponible(), 1)


if __name__ == "__main__":
    unittest.main()
