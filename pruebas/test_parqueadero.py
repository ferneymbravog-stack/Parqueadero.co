import os
import tempfile
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

    def test_registra_salida_y_libera_espacio(self):
        self.parqueadero.registrar_entrada(self.crear_vehiculo("ABC123"))
        numero_espacio, vehiculo = self.parqueadero.registrar_salida("ABC123")
        self.assertEqual(numero_espacio, 1)
        self.assertEqual(vehiculo.placa, "ABC123")
        self.assertEqual(self.parqueadero.cantidad_disponible(), 2)
        self.assertIsNone(self.parqueadero.buscar_vehiculo("ABC123"))

    def test_no_permite_salida_de_vehiculo_inexistente(self):
        with self.assertRaises(ValueError):
            self.parqueadero.registrar_salida("NOEXISTE")

    def test_calcula_tarifa_carro_por_tiempo(self):
        total = self.parqueadero.calcular_tarifa(
            "2026-10-21 09:00:00",
            "2026-10-21 11:15:00",
            "carro"
        )
        # 2 horas y 15 minutos se cobran como 3 horas (3 * 3000 = 9000)
        self.assertEqual(total, 9000)

    def test_calcula_tarifa_motocicleta_minimo_una_hora(self):
        total = self.parqueadero.calcular_tarifa(
            "2026-10-21 09:00:00",
            "2026-10-21 09:20:00",
            "motocicleta"
        )
        # 20 minutos se cobran como mínimo 1 hora (1 * 1500 = 1500)
        self.assertEqual(total, 1500)

    def test_guardar_y_recuperar_json(self):
        self.parqueadero.registrar_entrada(self.crear_vehiculo("ABC123"))
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = os.path.join(tmpdir, "parqueadero_test.json")
            self.parqueadero.guardar_en_json(ruta)

            nuevo_parqueadero = Parqueadero(2)
            cargado = nuevo_parqueadero.cargar_desde_json(ruta)
            self.assertTrue(cargado)
            self.assertEqual(nuevo_parqueadero.cantidad_disponible(), 1)
            espacio = nuevo_parqueadero.buscar_vehiculo("ABC123")
            self.assertIsNotNone(espacio)
            self.assertEqual(espacio.numero, 1)




if __name__ == "__main__":
    unittest.main()
