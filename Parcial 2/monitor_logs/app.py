import os, paramiko
from flask import Flask, render_template, request, jsonify
from monitor_logs.monitor_logs import generar_reporte
from monitor_logs.ssh_logs import leer_log_remoto

# python-dotenv es opcional — si no está, el formulario queda vacío
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

@app.route("/")
def index():
    # Precarga el formulario con valores de .env si existen
    valores_por_defecto = {
        "host":        os.getenv("LOG_HOST", ""),
        "usuario":     os.getenv("LOG_USER", ""),
        "ruta_remota": os.getenv("LOG_PATH", "/var/log/auth.log"),
    }
    return render_template("index.html", **valores_por_defecto)

@app.route("/analizar", methods=["POST"])
def analizar():
    datos = request.get_json()
    host        = datos.get("host")
    usuario     = datos.get("usuario")
    password    = datos.get("password")
    ruta_remota = datos.get("ruta_remota")

    if not all([host, usuario, password, ruta_remota]):
        return jsonify({"error": "Faltan campos del formulario"}), 400

    try:
        contenido = leer_log_remoto(host, usuario, password, ruta_remota)
    except paramiko.AuthenticationException:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
    except Exception as e:
        return jsonify({"error": f"Error al conectar o leer el log: {e}"}), 500

    # ruta_salida=None → no escribe a disco, solo regresa el dict
    reporte = generar_reporte(contenido=contenido, ruta_salida=None)
    return jsonify(reporte)

if __name__ == "__main__":
    app.run(debug=True)