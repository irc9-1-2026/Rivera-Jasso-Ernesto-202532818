import re, json
from collections import Counter

# Patrón: "2026-06-15 08:15:47 ERROR: mensaje..."
PATRON_LINEA = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+): (.+)$"
)
PATRON_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# --- Parsea texto ya leído (reutilizable para V1 y V2) ---
def parsear_texto(contenido):
    eventos = []
    for linea in contenido.splitlines():
        match = PATRON_LINEA.match(linea.strip())
        if match:
            eventos.append({
                "timestamp": match.group(1),
                "nivel":     match.group(2),
                "mensaje":   match.group(3),
            })
    return eventos

# ── Lee un archivo local y lo parsea (solo V1) ──────────────────
def parsear_log(ruta="servidor.log"):
    with open(ruta) as f:
        return parsear_texto(f.read())

# ── FASE 3: contar eventos por severidad ───────────────────────
def contar_por_nivel(eventos):
    niveles = [ev["nivel"] for ev in eventos]
    return dict(Counter(niveles))

# ── Detectar fuerza bruta: misma IP con 3+ logins fallidos ─────
def detectar_fuerza_bruta(eventos, umbral=3):
    ips_fallidas = []
    for ev in eventos:
        if ev["nivel"] == "ERROR" and "login fallido" in ev["mensaje"]:
            ip_match = PATRON_IP.search(ev["mensaje"])
            if ip_match:
                ips_fallidas.append(ip_match.group())
    conteo = Counter(ips_fallidas)
    return [ip for ip, n in conteo.items() if n >= umbral]

# --- FASE 4: generar reporte JSON ---
# Acepta `contenido` directo (string) o `ruta_log` (archivo).
# La V2 reutilizará esta misma función pasando el log traído por SSH.
def generar_reporte(ruta_log="servidor.log", ruta_salida="reporte.json", contenido=None):
    eventos = parsear_texto(contenido) if contenido is not None else parsear_log(ruta_log)
    reporte = {
        "total_eventos":     len(eventos),
        "eventos_por_nivel": contar_por_nivel(eventos),
        "ips_sospechosas":   detectar_fuerza_bruta(eventos),
    }
    if ruta_salida:
        with open(ruta_salida, "w") as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
    return reporte

if __name__ == "__main__":
    reporte = generar_reporte()
    print(json.dumps(reporte, indent=2, ensure_ascii=False))