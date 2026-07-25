import os
from datetime import datetime
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

load_dotenv()

app = Flask(__name__)

REQRES_API_KEY = os.getenv("REQRES_API_KEY")
LOCAL_API_URL = os.getenv(
    "LOCAL_API_URL",
    "http://api-dispositivos:5001/dispositivos",
)

SERVICIOS = [
    {"nombre": "GitHub", "url": "https://api.github.com"},
    {
        "nombre": "JSONPlaceholder",
        "url": "https://jsonplaceholder.typicode.com/posts/1",
    },
    {"nombre": "HTTPBingo", "url": "https://httpbingo.org/status/200"},
    {"nombre": "ReqRes", "url": "https://reqres.in/api/users/1"},
    {"nombre": "Mi API Local", "url": LOCAL_API_URL},
]


def construir_headers(url):
    """Agrega x-api-key solamente a las solicitudes dirigidas a ReqRes."""
    headers = {"User-Agent": "dashboard-docker/1.0"}
    dominio = urlparse(url).netloc.lower()

    if dominio.endswith("reqres.in") and REQRES_API_KEY:
        headers["x-api-key"] = REQRES_API_KEY

    return headers


def verificar_servicio(nombre, url):
    """Consulta un servicio y devuelve estado, código y latencia."""
    try:
        respuesta = requests.get(
            url,
            headers=construir_headers(url),
            timeout=5,
        )

        return {
            "nombre": nombre,
            "url": url,
            "activo": respuesta.status_code < 400,
            "status": respuesta.status_code,
            "latencia": round(
                respuesta.elapsed.total_seconds() * 1000,
                1,
            ),
            "error": None,
        }

    except requests.exceptions.Timeout:
        return {
            "nombre": nombre,
            "url": url,
            "activo": False,
            "status": None,
            "latencia": None,
            "error": "Timeout",
        }

    except requests.exceptions.RequestException as error:
        return {
            "nombre": nombre,
            "url": url,
            "activo": False,
            "status": None,
            "latencia": None,
            "error": str(error)[:80],
        }


@app.get("/health")
def health():
    """Healthcheck interno para Docker."""
    return jsonify({"status": "ok"}), 200


@app.get("/api/estado")
def estado():
    """Devuelve el diagnóstico de todos los servicios."""
    resultados = [
        verificar_servicio(servicio["nombre"], servicio["url"])
        for servicio in SERVICIOS
    ]

    activos = sum(1 for servicio in resultados if servicio["activo"])

    return jsonify(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(resultados),
            "activos": activos,
            "caidos": len(resultados) - activos,
            "servicios": resultados,
        }
    )


@app.get("/")
def index():
    """Sirve el dashboard web."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)