import json
import os

import requests
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env
load_dotenv()

BASE = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

# Validación para evitar ejecutar el programa sin configuración.
if not BASE or not API_KEY:
    raise RuntimeError(
        "Faltan BASE_URL o API_KEY. Revisa que exista el archivo .env "
        "y que contenga ambas variables."
    )

# Headers reutilizados en todas las peticiones.
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "practica2-reqres/1.0",
}

TIMEOUT = 15


# ── GET — listar usuarios ─────────────────────────────────────
def listar_usuarios(pagina=1):
    """Obtiene la lista de usuarios de la página indicada."""
    try:
        r = requests.get(
            f"{BASE}/users",
            params={"page": pagina},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        return r.json() if r.status_code == 200 else {"error": r.status_code}
    except requests.RequestException as error:
        return {"error": "No fue posible conectar con la API", "detalle": str(error)}


# ── POST — crear usuario ──────────────────────────────────────
def crear_usuario(nombre, puesto):
    """Crea un usuario simulado en ReqRes."""
    try:
        r = requests.post(
            f"{BASE}/users",
            json={"name": nombre, "job": puesto},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        return r.json() if r.status_code == 201 else {"error": r.status_code}
    except requests.RequestException as error:
        return {"error": "No fue posible conectar con la API", "detalle": str(error)}


# ── PUT — actualizar usuario ──────────────────────────────────
def actualizar_usuario(user_id, nombre, puesto):
    """Actualiza completamente un usuario simulado."""
    try:
        r = requests.put(
            f"{BASE}/users/{user_id}",
            json={"name": nombre, "job": puesto},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        return r.json() if r.status_code == 200 else {"error": r.status_code}
    except requests.RequestException as error:
        return {"error": "No fue posible conectar con la API", "detalle": str(error)}


# ── DELETE — eliminar usuario ─────────────────────────────────
def eliminar_usuario(user_id):
    """Elimina un usuario simulado."""
    try:
        r = requests.delete(
            f"{BASE}/users/{user_id}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        return {"ok": True} if r.status_code == 204 else {"error": r.status_code}
    except requests.RequestException as error:
        return {"error": "No fue posible conectar con la API", "detalle": str(error)}


if __name__ == "__main__":
    print(
        "Usuarios:",
        json.dumps(listar_usuarios(), indent=2, ensure_ascii=False),
    )
    print(
        "Nuevo:",
        json.dumps(
            crear_usuario("Ana Torres", "Network Engineer"),
            indent=2,
            ensure_ascii=False,
        ),
    )
    print(
        "Actualizado:",
        json.dumps(
            actualizar_usuario(2, "Ana Torres", "Senior NE"),
            indent=2,
            ensure_ascii=False,
        ),
    )
    print(
        "Eliminado:",
        json.dumps(eliminar_usuario(2), indent=2, ensure_ascii=False),
    )