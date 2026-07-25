import unittest
from unittest.mock import MagicMock, patch

import requests as req

from app import app, verificar_servicio


class TestDashboardDocker(unittest.TestCase):

    def test_servicio_activo(self):
        mock_respuesta = MagicMock()
        mock_respuesta.status_code = 200
        mock_respuesta.elapsed.total_seconds.return_value = 0.123

        with patch("app.requests.get", return_value=mock_respuesta):
            resultado = verificar_servicio("Test", "https://test.com")

        self.assertTrue(resultado["activo"])
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["latencia"], 123.0)

    def test_servicio_error_http(self):
        mock_respuesta = MagicMock()
        mock_respuesta.status_code = 500
        mock_respuesta.elapsed.total_seconds.return_value = 0.2

        with patch("app.requests.get", return_value=mock_respuesta):
            resultado = verificar_servicio("Test", "https://test.com")

        self.assertFalse(resultado["activo"])
        self.assertEqual(resultado["status"], 500)

    def test_servicio_timeout(self):
        with patch(
            "app.requests.get",
            side_effect=req.exceptions.Timeout,
        ):
            resultado = verificar_servicio("Test", "https://test.com")

        self.assertFalse(resultado["activo"])
        self.assertEqual(resultado["error"], "Timeout")

    def test_endpoint_estado(self):
        mock_respuesta = MagicMock()
        mock_respuesta.status_code = 200
        mock_respuesta.elapsed.total_seconds.return_value = 0.1

        with patch("app.requests.get", return_value=mock_respuesta):
            cliente = app.test_client()
            respuesta = cliente.get("/api/estado")

        datos = respuesta.get_json()

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(datos["total"], 5)
        self.assertEqual(datos["activos"], 5)
        self.assertEqual(datos["caidos"], 0)
        self.assertIn("timestamp", datos)
        self.assertIn("servicios", datos)

    def test_healthcheck(self):
        cliente = app.test_client()
        respuesta = cliente.get("/health")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()["status"], "ok")


if __name__ == "__main__":
    unittest.main(verbosity=2)