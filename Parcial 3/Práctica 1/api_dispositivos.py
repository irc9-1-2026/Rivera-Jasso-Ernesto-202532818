from flask import Flask, jsonify, request

app = Flask(__name__)

# Base de datos en memoria (lista de diccionarios)
dispositivos = [
    {
        "id": 1,
        "nombre": "SW-Core-01",
        "tipo": "switch",
        "ip": "10.0.0.1",
        "estado": "activo",
    },
    {
        "id": 2,
        "nombre": "RT-Edge-01",
        "tipo": "router",
        "ip": "10.0.0.2",
        "estado": "activo",
    },
    {
        "id": 3,
        "nombre": "FW-DMZ-01",
        "tipo": "firewall",
        "ip": "10.0.0.3",
        "estado": "inactivo",
    },
]

siguiente_id = 4  # Contador para asignar nuevos IDs


# ── GET /dispositivos — listar todos ──────────────────────────
@app.route("/dispositivos", methods=["GET"])
def listar():
    """Devuelve todos los dispositivos registrados."""
    return jsonify(dispositivos), 200


# ── GET /dispositivos/<id> — buscar uno ──────────────────────
@app.route("/dispositivos/<int:device_id>", methods=["GET"])
def obtener(device_id):
    """Busca un dispositivo mediante su ID."""
    disp = next((d for d in dispositivos if d["id"] == device_id), None)

    if disp is None:
        return jsonify({"error": "Dispositivo no encontrado"}), 404

    return jsonify(disp), 200


# ── POST /dispositivos — agregar nuevo ────────────────────────
@app.route("/dispositivos", methods=["POST"])
def agregar():
    """Agrega un dispositivo nuevo utilizando los datos del cuerpo JSON."""
    global siguiente_id

    datos = request.get_json()

    nuevo = {
        "id": siguiente_id,
        "nombre": datos.get("nombre", "Sin nombre"),
        "tipo": datos.get("tipo", "desconocido"),
        "ip": datos.get("ip", "0.0.0.0"),
        "estado": datos.get("estado", "activo"),
    }

    dispositivos.append(nuevo)
    siguiente_id += 1

    return jsonify(nuevo), 201


# ── PUT /dispositivos/<id> — actualizar completo ─────────────
@app.route("/dispositivos/<int:device_id>", methods=["PUT"])
def actualizar(device_id):
    """Actualiza los datos de un dispositivo existente."""
    disp = next((d for d in dispositivos if d["id"] == device_id), None)

    if disp is None:
        return jsonify({"error": "No encontrado"}), 404

    datos = request.get_json()

    disp["nombre"] = datos.get("nombre", disp["nombre"])
    disp["tipo"] = datos.get("tipo", disp["tipo"])
    disp["ip"] = datos.get("ip", disp["ip"])
    disp["estado"] = datos.get("estado", disp["estado"])

    return jsonify(disp), 200


# ── DELETE /dispositivos/<id> — eliminar ─────────────────────
@app.route("/dispositivos/<int:device_id>", methods=["DELETE"])
def eliminar(device_id):
    """Elimina un dispositivo mediante su ID."""
    global dispositivos

    original = len(dispositivos)
    dispositivos = [d for d in dispositivos if d["id"] != device_id]

    if len(dispositivos) == original:
        return jsonify({"error": "No encontrado"}), 404

    return "", 204


if __name__ == "__main__":
    app.run(debug=True)