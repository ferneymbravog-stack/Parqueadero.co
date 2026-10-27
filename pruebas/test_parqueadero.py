import csv
import io
import os
import tempfile
import unittest
from unittest.mock import patch
from modelos.parqueadero import Parqueadero
from modelos.vehiculo import Vehiculo
from servicios.servicio_entradas import validar_placa, registrar_entrada
from servicios.servicio_salidas import registrar_salida
from servicios.servicio_consultas import consultar_por_placa, exportar_csv


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
            # Verifica que el archivo fue reparado y ahora sí carga correctamente
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
        self.assertEqual(informe["ocupacion_por_tipo"]["carro"], 1)
        self.assertEqual(informe["ocupacion_por_tipo"]["motocicleta"], 0)

    def test_genera_informe_ingresos(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro", "2026-10-24 08:00:00"))
        self.parqueadero.registrar_entrada(Vehiculo("MOTO99", "motocicleta", "2026-10-24 09:00:00"))

        espacio_carro, carro = self.parqueadero.registrar_salida("ABC123")
        self.parqueadero.registrar_historial_salida(espacio_carro, carro, "2026-10-24 10:00:00")

        espacio_moto, moto = self.parqueadero.registrar_salida("MOTO99")
        self.parqueadero.registrar_historial_salida(espacio_moto, moto, "2026-10-24 09:30:00")

        informe = self.parqueadero.obtener_informe_ingresos()
        self.assertEqual(informe["total_salidas"], 2)
        self.assertEqual(informe["horas_totales_cobradas"], 3)  # 2h carro + 1h moto
        self.assertEqual(informe["ingresos_totales"], 7500)     # 6000 carro + 1500 moto
        self.assertEqual(informe["ingresos_por_tipo"]["carro"], 6000)
        self.assertEqual(informe["ingresos_por_tipo"]["motocicleta"], 1500)

    def test_filtrar_ingresos_por_fecha(self):
        self.parqueadero.registrar_entrada(Vehiculo("DIA100", "carro", "2026-10-24 08:00:00"))
        esp1, v1 = self.parqueadero.registrar_salida("DIA100")
        self.parqueadero.registrar_historial_salida(esp1, v1, "2026-10-24 09:00:00")

        self.parqueadero.registrar_entrada(Vehiculo("DIA200", "motocicleta", "2026-10-25 10:00:00"))
        esp2, v2 = self.parqueadero.registrar_salida("DIA200")
        self.parqueadero.registrar_historial_salida(esp2, v2, "2026-10-25 11:30:00")

        informe_dia_24 = self.parqueadero.obtener_informe_ingresos(fecha="2026-10-24")
        self.assertEqual(informe_dia_24["total_salidas"], 1)
        self.assertEqual(informe_dia_24["ingresos_totales"], 3000)

        informe_dia_25 = self.parqueadero.obtener_informe_ingresos(fecha="2026-10-25")
        self.assertEqual(informe_dia_25["total_salidas"], 1)
        self.assertEqual(informe_dia_25["ingresos_totales"], 3000)

        with self.assertRaises(ValueError):
            self.parqueadero.obtener_informe_ingresos(fecha="fecha-invalida")

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
            self.assertEqual(filas[1]["total_pagar"], "1500")

    def test_exportar_reporte_csv(self):
        self.parqueadero.registrar_entrada(Vehiculo("ABC123", "carro", "2026-10-24 08:00:00"))
        espacio_carro, carro = self.parqueadero.registrar_salida("ABC123")
        self.parqueadero.registrar_historial_salida(espacio_carro, carro, "2026-10-24 09:30:00")

        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_csv = os.path.join(tmpdir, "reporte.csv")
            exportado = self.parqueadero.exportar_reporte_csv(ruta_csv)
            self.assertTrue(exportado)
            self.assertTrue(os.path.exists(ruta_csv))

            with open(ruta_csv, mode="r", encoding="utf-8") as archivo:
                filas = {fila["indicador"]: fila["valor"] for fila in csv.DictReader(archivo)}

            self.assertEqual(filas["Capacidad total"], "2")
            self.assertEqual(filas["Total salidas atendidas"], "1")
            self.assertEqual(filas["Ingresos totales recaudados"], "6000")

    def test_validacion_placas_con_guiones(self):
        self.assertEqual(validar_placa("abc-541"), "ABC-541")
        with self.assertRaises(ValueError):
            validar_placa("-ABC123")
        with self.assertRaises(ValueError):
            validar_placa("ABC--123")

    def test_flujo_funcional_completo_extremo_a_extremo(self):
        """Prueba funcional: entradas, consultas, salidas, persistencia JSON, informes y exportación CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_json = os.path.join(tmpdir, "parqueadero.json")
            ruta_reg_csv = os.path.join(tmpdir, "registros.csv")
            ruta_rep_csv = os.path.join(tmpdir, "reporte.csv")

            parqueadero = Parqueadero(3)

            # 1. Registrar entrada de un carro y una moto
            espacio_1 = parqueadero.registrar_entrada(Vehiculo("CAR-101", "carro", "2026-10-25 08:00:00"))
            espacio_2 = parqueadero.registrar_entrada(Vehiculo("MOT-202", "moto", "2026-10-25 08:30:00"))
            self.assertEqual((espacio_1, espacio_2), (1, 2))
            self.assertEqual(parqueadero.cantidad_disponible(), 1)

            # 2. Guardar estado en JSON y recargarlo en una nueva instancia
            self.assertTrue(parqueadero.guardar_en_json(ruta_json))
            parqueadero_recargado = Parqueadero(3)
            self.assertTrue(parqueadero_recargado.cargar_desde_json(ruta_json))
            self.assertEqual(parqueadero_recargado.cantidad_disponible(), 1)

            # 3. Registrar salida del carro tras 1h 30m (2 horas cobradas = $6,000)
            num_espacio, vehiculo_saliente = parqueadero_recargado.registrar_salida("CAR-101")
            cobro = parqueadero_recargado.registrar_historial_salida(
                num_espacio, vehiculo_saliente, "2026-10-25 09:30:00"
            )
            self.assertEqual(cobro["horas_cobradas"], 2)
            self.assertEqual(cobro["total_pagar"], 6000)

            # 4. Verificar informes de ocupación e ingresos
            ocupacion = parqueadero_recargado.obtener_informe_ocupacion()
            ingresos = parqueadero_recargado.obtener_informe_ingresos()
            self.assertEqual(ocupacion["espacios_ocupados"], 1)
            self.assertEqual(ocupacion["ocupacion_por_tipo"]["motocicleta"], 1)
            self.assertEqual(ingresos["ingresos_totales"], 6000)

            # 5. Exportar todo a CSV y comprobar archivos
            self.assertTrue(parqueadero_recargado.exportar_todo_csv(ruta_reg_csv, ruta_rep_csv))
            self.assertTrue(os.path.exists(ruta_reg_csv))
            self.assertTrue(os.path.exists(ruta_rep_csv))

    def test_servicios_interactivos_con_mock_input(self):
        """Prueba funcional de los servicios de consola simulando entradas del usuario."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parqueadero = Parqueadero(2)
            # Evitar que sobrescriba el archivo real durante la prueba interactiva
            with patch.object(parqueadero, "guardar_en_json", return_value=True):
                with patch("builtins.input", side_effect=["XYZ-987", "carro", ""]), patch("sys.stdout", new_callable=io.StringIO):
                    registrar_entrada(parqueadero)

                self.assertIsNotNone(parqueadero.buscar_vehiculo("XYZ-987"))

                with patch("builtins.input", side_effect=["XYZ-987", ""]), patch("sys.stdout", new_callable=io.StringIO) as salida_consulta:
                    consultar_por_placa(parqueadero)
                    self.assertIn("está estacionado en el espacio 1", salida_consulta.getvalue())

                with patch("builtins.input", side_effect=["XYZ-987", ""]), patch("sys.stdout", new_callable=io.StringIO) as salida_cobro:
                    registrar_salida(parqueadero)
                    self.assertIn("TOTAL A PAGAR", salida_cobro.getvalue())

                self.assertIsNone(parqueadero.buscar_vehiculo("XYZ-987"))
                self.assertEqual(len(parqueadero.historial_salidas), 1)


if __name__ == "__main__":
    unittest.main()
