import json

import requests

BASE = "http://localhost:5000/dispositivos"


# ── GET — buscar todos los dispositivos ──────────────────────
def listar_dispositivos():
    """Obtiene la lista completa de dispositivos."""
    r = requests.get(BASE)

    if r.status_code == 200:
        return r.json()

    return {"error": r.status_code}


# ── GET — buscar uno por ID ───────────────────────────────────
def buscar_dispositivo(device_id):
    """Obtiene un dispositivo específico por su ID."""
    r = requests.get(f"{BASE}/{device_id}")
    return r.json(), r.status_code


# ── POST — agregar dispositivo nuevo ─────────────────────────
def agregar_dispositivo(nombre, tipo, ip, estado="activo"):
    """Envía un dispositivo nuevo a la API."""
    nuevo = {
        "nombre": nombre,
        "tipo": tipo,
        "ip": ip,
        "estado": estado,
    }

    r = requests.post(BASE, json=nuevo)
    return r.json(), r.status_code


# ── PUT — actualizar dispositivo completo ─────────────────────
def actualizar_dispositivo(device_id, nombre, tipo, ip, estado):
    """Actualiza un dispositivo existente."""
    r = requests.put(
        f"{BASE}/{device_id}",
        json={
            "nombre": nombre,
            "tipo": tipo,
            "ip": ip,
            "estado": estado,
        },
    )

    return r.json(), r.status_code


# ── DELETE — eliminar dispositivo ─────────────────────────────
def eliminar_dispositivo(device_id):
    """Elimina un dispositivo mediante su ID."""
    r = requests.delete(f"{BASE}/{device_id}")

    if r.status_code == 204:
        return {"ok": True, "eliminado": device_id}

    return r.json(), r.status_code


# ── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== GET todos ===")
    print(json.dumps(listar_dispositivos(), indent=2, ensure_ascii=False))

    print("\n=== GET uno (id=1) ===")
    datos, status = buscar_dispositivo(1)
    print(
        f"Status: {status}",
        json.dumps(datos, indent=2, ensure_ascii=False),
    )

    print("\n=== POST nuevo dispositivo ===")
    nuevo, status = agregar_dispositivo(
        "AP-Piso2",
        "access-point",
        "192.168.1.50",
    )
    print(
        f"Status: {status}",
        json.dumps(nuevo, indent=2, ensure_ascii=False),
    )

    print("\n=== PUT actualizar id=2 ===")
    act, status = actualizar_dispositivo(
        2,
        "RT-Edge-01-UPD",
        "router",
        "10.0.0.20",
        "activo",
    )
    print(
        f"Status: {status}",
        json.dumps(act, indent=2, ensure_ascii=False),
    )

    print("\n=== DELETE id=3 ===")
    print(eliminar_dispositivo(3))

    print("\n=== GET todos (verificar cambios) ===")
    print(json.dumps(listar_dispositivos(), indent=2, ensure_ascii=False))