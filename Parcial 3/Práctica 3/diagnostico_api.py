import json
import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

# Carga las variables del archivo .env.
load_dotenv()

API_KEY = os.getenv("API_KEY")
TIMEOUT = 8


# ── Clasificar un código de estado por categoría ──────────────
def clasificar_status(codigo):
    """Devuelve un dict con categoría, nombre y acción sugerida."""
    if 100 <= codigo <= 199:
        return {
            "categoria": "1xx",
            "tipo": "Informativo",
            "accion": "Esperar la respuesta final del servidor",
        }
    if 200 <= codigo <= 299:
        return {
            "categoria": "2xx",
            "tipo": "Éxito",
            "accion": "Procesar la respuesta normalmente",
        }
    if 300 <= codigo <= 399:
        return {
            "categoria": "3xx",
            "tipo": "Redirección",
            "accion": "Seguir la redirección o actualizar la URL",
        }
    if codigo == 400:
        return {
            "categoria": "4xx",
            "tipo": "Bad Request",
            "accion": "Revisar los datos, parámetros y formato JSON enviados",
        }
    if codigo == 401:
        return {
            "categoria": "4xx",
            "tipo": "Unauthorized",
            "accion": "Verificar la API Key, token o credenciales",
        }
    if codigo == 403:
        return {
            "categoria": "4xx",
            "tipo": "Forbidden",
            "accion": "Verificar permisos del token o usuario",
        }
    if codigo == 404:
        return {
            "categoria": "4xx",
            "tipo": "Not Found",
            "accion": "Verificar la URL o el ID; el recurso no existe",
        }
    if codigo == 429:
        return {
            "categoria": "4xx",
            "tipo": "Too Many Requests",
            "accion": "Esperar antes de reintentar (rate limit)",
        }
    if 400 <= codigo <= 499:
        return {
            "categoria": "4xx",
            "tipo": "Error del cliente",
            "accion": "Revisar la petición y consultar la documentación de la API",
        }
    if 500 <= codigo <= 599:
        return {
            "categoria": "5xx",
            "tipo": "Error del servidor",
            "accion": "El problema está en el servidor, no en tu código. Reportar.",
        }

    return {
        "categoria": "desconocido",
        "tipo": "?",
        "accion": "Consultar documentación",
    }


def construir_headers(url, headers=None):
    """
    Construye los headers de la petición.

    ReqRes exige x-api-key. Para las demás páginas se conservan únicamente
    los headers proporcionados por el usuario.
    """
    headers_finales = dict(headers or {})
    dominio = urlparse(url).netloc.lower()

    if dominio.endswith("reqres.in"):
        if not API_KEY:
            raise ValueError(
                "Falta API_KEY. Crea un archivo .env y coloca tu clave de ReqRes."
            )

        headers_finales.setdefault("x-api-key", API_KEY)
        headers_finales.setdefault("Content-Type", "application/json")
        headers_finales.setdefault("User-Agent", "practica3-diagnostico/1.0")

    return headers_finales


# ── Hacer petición y generar registro de diagnóstico ──────────
def diagnosticar_url(metodo, url, **kwargs):
    """Realiza la petición y devuelve un dict con todo el diagnóstico."""
    metodo = metodo.upper()

    try:
        headers = construir_headers(url, kwargs.pop("headers", None))

        # No seguir redirecciones permite observar directamente códigos 3xx.
        kwargs.setdefault("allow_redirects", False)

        r = requests.request(
            metodo,
            url,
            headers=headers,
            timeout=TIMEOUT,
            **kwargs,
        )

        info = clasificar_status(r.status_code)

        return {
            "url": url,
            "metodo": metodo,
            "status": r.status_code,
            "categoria": info["categoria"],
            "tipo": info["tipo"],
            "accion": info["accion"],
            "exitoso": 200 <= r.status_code <= 299,
        }

    except ValueError as error:
        return {
            "url": url,
            "metodo": metodo,
            "error": "Configuración",
            "detalle": str(error),
            "accion": "Revisar el archivo .env",
            "exitoso": False,
        }

    except requests.exceptions.Timeout:
        return {
            "url": url,
            "metodo": metodo,
            "error": "Timeout",
            "accion": "Reintentar y verificar la disponibilidad del servidor",
            "exitoso": False,
        }

    except requests.exceptions.ConnectionError:
        return {
            "url": url,
            "metodo": metodo,
            "error": "Sin conexión",
            "accion": "Verificar red y URL",
            "exitoso": False,
        }

    except requests.exceptions.RequestException as error:
        return {
            "url": url,
            "metodo": metodo,
            "error": "Error de petición",
            "detalle": str(error),
            "accion": "Revisar la petición y la configuración de red",
            "exitoso": False,
        }


# ── Generar la tabla de diagnóstico en JSON ───────────────────
def generar_tabla_diagnostico(pruebas, archivo_salida="diagnostico.json"):
    """
    Ejecuta todas las pruebas y guarda el diagnóstico en formato JSON.

    Cada prueba debe tener "metodo" y "url". También puede incluir argumentos
    aceptados por requests, por ejemplo: json, params o headers.
    """
    resultados = []

    for prueba in pruebas:
        metodo = prueba["metodo"]
        url = prueba["url"]

        # Los campos adicionales se pasan a diagnosticar_url().
        opciones = {
            clave: valor
            for clave, valor in prueba.items()
            if clave not in {"metodo", "url"}
        }

        resultado = diagnosticar_url(metodo, url, **opciones)
        resultados.append(resultado)

        estado = "✅" if resultado.get("exitoso") else "❌"
        status = resultado.get("status", "ERR")
        print(f"{estado} {resultado['metodo']:6} {status} — {resultado['url']}")

    exitosas = sum(
        1 for resultado in resultados if resultado.get("exitoso") is True
    )

    tabla = {
        "total_pruebas": len(resultados),
        "exitosas": exitosas,
        "fallidas": len(resultados) - exitosas,
        "resultados": resultados,
    }

    with open(archivo_salida, "w", encoding="utf-8") as archivo:
        json.dump(tabla, archivo, indent=2, ensure_ascii=False)

    return tabla


if __name__ == "__main__":
    pruebas = [
        {
            "metodo": "GET",
            "url": "https://reqres.in/api/users/1",
        },
        {
            "metodo": "GET",
            "url": "https://reqres.in/api/users/9999",
        },
        {
            "metodo": "POST",
            "url": "https://reqres.in/api/users",
            "json": {
                "name": "Ana Torres",
                "job": "Network Engineer",
            },
        },
        {
            "metodo": "DELETE",
            "url": "https://reqres.in/api/users/2",
        },
        {
            "metodo": "GET",
            "url": "https://httpstat.us/500",
        },
        {
            "metodo": "GET",
            "url": "https://httpstat.us/401",
        },

        # Pruebas adicionales del checklist:
        # {"metodo": "GET", "url": "https://httpstat.us/429"},
        # {"metodo": "GET", "url": "https://url-que-no-existe.xyz"},
    ]

    tabla = generar_tabla_diagnostico(pruebas)

    resumen = {
        "total": tabla["total_pruebas"],
        "exitosas": tabla["exitosas"],
        "fallidas": tabla["fallidas"],
    }

    print("\nResumen:", json.dumps(resumen, indent=2, ensure_ascii=False))