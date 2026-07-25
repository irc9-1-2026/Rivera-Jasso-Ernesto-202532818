import unittest
from unittest.mock import MagicMock, patch

import requests as req
from app import app, verificar_servicio


class TestDashboard(unittest.TestCase):

    def test_servicio_activo(self):
        mock_r = MagicMock()
        mock_r.status_code = 200
        mock_r.elapsed.total_seconds.return_value = 0.123
        with patch("app.requests.get", return_value=mock_r):
            resultado = verificar_servicio("Test", "https://test.com")
        self.assertTrue(resultado["activo"])
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["latencia"], 123.0)

    def test_servicio_caido_timeout(self):
        with patch("app.requests.get", side_effect=req.exceptions.Timeout):
            resultado = verificar_servicio("Test", "https://test.com")
        self.assertFalse(resultado["activo"])
        self.assertEqual(resultado["error"], "Timeout")

    def test_endpoint_estado(self):
        mock_r = MagicMock()
        mock_r.status_code = 200
        mock_r.elapsed.total_seconds.return_value = 0.1
        with patch("app.requests.get", return_value=mock_r):
            cliente = app.test_client()
            respuesta = cliente.get("/api/estado")
        datos = respuesta.get_json()
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("servicios", datos)
        self.assertIn("timestamp", datos)
        self.assertEqual(datos["total"], 5)
        self.assertEqual(datos["activos"], 5)

    def test_servicio_error_http(self):
        mock_r = MagicMock()
        mock_r.status_code = 500
        mock_r.elapsed.total_seconds.return_value = 0.2
        with patch("app.requests.get", return_value=mock_r):
            resultado = verificar_servicio("Test", "https://test.com")
        self.assertFalse(resultado["activo"])
        self.assertEqual(resultado["status"], 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)