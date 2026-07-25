from flask import Flask, jsonify, request

app = Flask(__name__)

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

siguiente_id = 4


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/dispositivos")
def listar():
    return jsonify(dispositivos), 200


@app.get("/dispositivos/<int:device_id>")
def obtener(device_id):
    dispositivo = next(
        (item for item in dispositivos if item["id"] == device_id),
        None,
    )

    if dispositivo is None:
        return jsonify({"error": "Dispositivo no encontrado"}), 404

    return jsonify(dispositivo), 200


@app.post("/dispositivos")
def agregar():
    global siguiente_id

    datos = request.get_json(silent=True) or {}

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


@app.put("/dispositivos/<int:device_id>")
def actualizar(device_id):
    dispositivo = next(
        (item for item in dispositivos if item["id"] == device_id),
        None,
    )

    if dispositivo is None:
        return jsonify({"error": "No encontrado"}), 404

    datos = request.get_json(silent=True) or {}

    for campo in ("nombre", "tipo", "ip", "estado"):
        dispositivo[campo] = datos.get(campo, dispositivo[campo])

    return jsonify(dispositivo), 200


@app.delete("/dispositivos/<int:device_id>")
def eliminar(device_id):
    global dispositivos

    cantidad_original = len(dispositivos)
    dispositivos = [
        item for item in dispositivos if item["id"] != device_id
    ]

    if len(dispositivos) == cantidad_original:
        return jsonify({"error": "No encontrado"}), 404

    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)