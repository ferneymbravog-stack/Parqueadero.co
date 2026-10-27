import csv
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
        self.assertEqual(total, 9000)

    def test_calcula_tarifa_motocicleta_minimo_una_hora(self):
        total = self.parqueadero.calcular_tarifa(
            "2026-10-21 09:00:00",
            "2026-10-21 09:20:00",
            "motocicleta"
        )
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

    def test_cargar_json_inexistente_inicializa_archivo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = os.path.join(tmpdir, "no_existe.json")
            cargado = self.parqueadero.cargar_desde_json(ruta)
            self.assertFalse(cargado)
            self.assertTrue(os.path.exists(ruta))
            self.assertEqual(self.parqueadero.cantidad_disponible(), 2)

    def test_cargar_json_danado_no_detiene_sistema_y_repara_archivo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = os.path.join(tmpdir, "corrupto.json")
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write("{archivo_json_danado: [sin_cerrar")

            cargado = self.parqueadero.cargar_desde_json(ruta)
            self.assertFalse(cargado)
            self.assertEqual(self.parqueadero.cantidad_disponible(), 2)
            self.assertTrue(self.parqueadero.cargar_desde_json(ruta))

    def test_cargar_json_vacio_se_recupera(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = os.path.join(tmpdir, "vacio.json")
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write("")

            cargado = self.parqueadero.cargar_desde_json(ruta)
            self.assertFalse(cargado)
            self.assertEqual(self.parqueadero.cantidad_disponible(), 2)

    def test_cargar_json_estructura_invalida_se_recupera(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = os.path.join(tmpdir, "estructura_invalida.json")
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write('{"espacios_ocupados": [{"numero": "uno", "placa": ""}]}')

            cargado = self.parqueadero.cargar_desde_json(ruta)
            self.assertFalse(cargado)
            self.assertEqual(self.parqueadero.cantidad_disponible(), 2)

    def test_genera_informe_ocupacion(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro", "2026-10-24 08:00:00"))
        informe = self.parqueadero.obtener_informe_ocupacion()

        self.assertEqual(informe["capacidad_total"], 2)
        self.assertEqual(informe["espacios_ocupados"], 1)
        self.assertEqual(informe["espacios_disponibles"], 1)
        self.assertEqual(informe["porcentaje_ocupacion"], 50.0)

    def test_genera_informe_ingresos(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro", "2026-10-24 08:00:00"))
        self.parqueadero.registrar_entrada(Vehiculo("MOTO99", "motocicleta", "2026-10-24 09:00:00"))

        espacio_carro, carro = self.parqueadero.registrar_salida("ABC123")
        self.parqueadero.registrar_historial_salida(espacio_carro, carro, "2026-10-24 10:00:00")

        espacio_moto, moto = self.parqueadero.registrar_salida("MOTO99")
        self.parqueadero.registrar_historial_salida(espacio_moto, moto, "2026-10-24 09:30:00")

        informe = self.parqueadero.obtener_informe_ingresos()
        self.assertEqual(informe["total_salidas"], 2)
        self.assertEqual(informe["ingresos_totales"], 7500)

    def test_filtrar_ingresos_por_fecha(self):
        self.parqueadero.registrar_entrada(Vehiculo("DIA100", "carro", "2026-10-24 08:00:00"))
        esp1, v1 = self.parqueadero.registrar_salida("DIA100")
        self.parqueadero.registrar_historial_salida(esp1, v1, "2026-10-24 09:00:00")

        informe_dia_24 = self.parqueadero.obtener_informe_ingresos(fecha="2026-10-24")
        self.assertEqual(informe_dia_24["total_salidas"], 1)
        self.assertEqual(informe_dia_24["ingresos_totales"], 3000)

    def test_exportar_registros_csv(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro", "2026-10-24 08:00:00"))
        self.parqueadero.registrar_entrada(Vehiculo("MOTO99", "motocicleta", "2026-10-24 09:00:00"))
        espacio_moto, moto = self.parqueadero.registrar_salida("MOTO99")
        self.parqueadero.registrar_historial_salida(espacio_moto, moto, "2026-10-24 09:45:00")

        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_csv = os.path.join(tmpdir, "registros.csv")
            exportado = self.parqueadero.exportar_registros_csv(ruta_csv)
            self.assertTrue(exportado)
            self.assertTrue(os.path.exists(ruta_csv))

            with open(ruta_csv, mode="r", encoding="utf-8") as archivo:
                filas = list(csv.DictReader(archivo))

            self.assertEqual(len(filas), 2)
            self.assertEqual(filas[0]["placa"], "ABC123")
            self.assertEqual(filas[0]["estado"], "Estacionado")
            self.assertEqual(filas[1]["placa"], "MOTO99")
            self.assertEqual(filas[1]["estado"], "Finalizado")

    def test_exportar_reporte_csv(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro", "2026-10-24 08:00:00"))
        espacio_carro, carro = self.parqueadero.registrar_salida("ABC123")
        self.parqueadero.registrar_historial_salida(espacio_carro, carro, "2026-10-24 09:30:00")

        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_csv = os.path.join(tmpdir, "reporte.csv")
            exportado = self.parqueadero.exportar_reporte_csv(ruta_csv)
            self.assertTrue(exportado)
            self.assertTrue(os.path.exists(ruta_csv))


if __name__ == "__main__":
    unittest.main()
