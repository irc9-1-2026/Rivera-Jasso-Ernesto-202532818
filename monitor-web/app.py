from flask import Flask, render_template, jsonify, send_file
import psutil
import platform
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

historial = []


def top_procesos(n=5):
    procesos = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            procesos.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": proc.info['cpu_percent'] or 0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return sorted(procesos, key=lambda p: p['cpu_percent'], reverse=True)[:n]


def obtener_datos():
    ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    datos = {
        "os": platform.system(),
        "version_os": platform.release(),
        "arquitectura": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "cpu": psutil.cpu_percent(interval=1),
        "memoria": psutil.virtual_memory().percent,
        "fecha": ahora,
        "procesos": top_procesos()
    }

    historial.append({
        "fecha": ahora,
        "cpu": datos["cpu"],
        "memoria": datos["memoria"]
    })

    if len(historial) > 20:
        historial.pop(0)

    return datos


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/datos")
def datos():
    datos_actuales = obtener_datos()
    datos_actuales["historial"] = historial
    return jsonify(datos_actuales)


@app.route("/reporte")
def generar_reporte():
    archivo_pdf = "reporte_monitor.pdf"

    c = canvas.Canvas(archivo_pdf, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Reporte del Monitor de Sistema")

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 80, f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    y = height - 120

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Información del sistema")
    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Sistema operativo: {platform.system()} {platform.release()}")
    y -= 18
    c.drawString(50, y, f"Arquitectura: {platform.machine()}")
    y -= 18
    c.drawString(50, y, f"Hostname: {platform.node()}")
    y -= 18
    c.drawString(50, y, f"Versión de Python: {platform.python_version()}")
    y -= 35

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Historial de recursos")
    y -= 25

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Fecha y hora")
    c.drawString(220, y, "CPU %")
    c.drawString(300, y, "RAM %")
    y -= 15

    c.setFont("Helvetica", 10)

    for registro in historial:
        if y < 80:
            c.showPage()
            y = height - 50

        c.drawString(50, y, registro["fecha"])
        c.drawString(220, y, str(registro["cpu"]))
        c.drawString(300, y, str(registro["memoria"]))
        y -= 15

    c.save()

    return send_file(archivo_pdf, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)