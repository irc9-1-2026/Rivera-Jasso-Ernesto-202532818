import psutil       # Info del sistema: CPU, RAM, procesos
import platform     # Info del SO: nombre, versión, arquitectura
import datetime     # Fecha y hora
import time         # Para pausas entre actualizaciones
import os           # Para limpiar la pantalla


# ============================================================
#  CONSTANTES
#  Variables que no cambian durante la ejecución
# ============================================================
INTERVALO_SEGUNDOS  = 5    # Cada cuántos segundos se refresca
TOP_PROCESOS        = 10   # Cuántos procesos mostrar


# ============================================================
#  FUNCIÓN: Limpiar pantalla
#  En Shell:  clear (Linux/Mac) o cls (Windows)
# ============================================================
def limpiar_pantalla():
    # os.name == 'nt' significa que estamos en Windows
    os.system('cls' if os.name == 'nt' else 'clear')


# ============================================================
#  FUNCIÓN: Línea separadora decorativa
# ============================================================
def separador(caracter='─', ancho=60):
    print(caracter * ancho)


# ============================================================
#  FUNCIÓN: Información del sistema operativo
#  Similar a: Get-ComputerInfo | uname -a
# ============================================================
def mostrar_info_sistema():
    separador('═')
    print("  INFORMACIÓN DEL SISTEMA")
    separador('═')

    # platform nos da datos del SO donde corre Python
    print(f"  Sistema operativo : {platform.system()} {platform.release()}")
    print(f"  Hostname          : {platform.node()}")
    print(f"  Arquitectura      : {platform.machine()}")
    print(f"  Versión de Python : {platform.python_version()}")

    separador()


# ============================================================
#  FUNCIÓN: Uso de CPU
#  Similar a: Get-Counter '\Processor(_Total)\% Processor Time'
#
#  psutil.cpu_percent(interval=1) toma una muestra de 1 segundo
#  para calcular el porcentaje — más preciso que tomar al instante
# ============================================================
def mostrar_cpu():
    porcentaje = psutil.cpu_percent(interval=1)
    nucleos    = psutil.cpu_count(logical=True)

    # Construimos una barra visual con caracteres
    # Ejemplo: [████████░░░░░░░░░░░░] 40%
    bloques_total  = 30
    bloques_llenos = int((porcentaje / 100) * bloques_total)
    barra = '█' * bloques_llenos + '░' * (bloques_total - bloques_llenos)

    print(f"\n  CPU")
    print(f"  Núcleos : {nucleos}")
    print(f"  Uso     : [{barra}] {porcentaje:.1f}%")

    # Alerta si el CPU está muy alto
    if porcentaje >= 85:
        print("  ⚠  ALERTA: CPU muy alto")
    elif porcentaje >= 60:
        print("  ↑  CPU moderado")


# ============================================================
#  FUNCIÓN: Uso de RAM
#  Similar a: Get-WmiObject Win32_OperatingSystem
#
#  Los valores de psutil vienen en BYTES, convertimos a GB
#  dividiendo entre 1024^3
# ============================================================
def mostrar_ram():
    ram = psutil.virtual_memory()

    # Convertir bytes → gigabytes
    total_gb    = ram.total    / (1024 ** 3)
    usada_gb    = ram.used     / (1024 ** 3)
    libre_gb    = ram.available / (1024 ** 3)
    porcentaje  = ram.percent

    bloques_total  = 30
    bloques_llenos = int((porcentaje / 100) * bloques_total)
    barra = '█' * bloques_llenos + '░' * (bloques_total - bloques_llenos)

    print(f"\n  RAM")
    print(f"  Total  : {total_gb:.1f} GB")
    print(f"  Usada  : {usada_gb:.1f} GB")
    print(f"  Libre  : {libre_gb:.1f} GB")
    print(f"  Uso    : [{barra}] {porcentaje:.1f}%")

    if porcentaje >= 85:
        print("  ⚠  ALERTA: RAM muy alta")


# ============================================================
#  FUNCIÓN: Top N procesos por uso de CPU
#  Similar a: Get-Process | Sort-Object CPU -Descending | Select -First 10
#             ps aux --sort=-%cpu | head -11
#
#  process_iter(['pid','name','cpu_percent','memory_percent'])
#  itera sobre todos los procesos activos y extrae esos campos
# ============================================================
def mostrar_procesos():
    procesos = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procesos.append({
                'pid':  proc.info['pid'],
                'nombre': proc.info['name'],
                'cpu':  proc.info['cpu_percent']    or 0,
                'ram':  proc.info['memory_percent'] or 0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Algunos procesos del sistema no permiten ser leídos
            # En Shell también ocurre con procesos de sistema
            pass

    # Ordenar por CPU de mayor a menor (similar a Sort-Object -Descending)
    procesos_ordenados = sorted(procesos, key=lambda p: p['cpu'], reverse=True)
    top = procesos_ordenados[:TOP_PROCESOS]

    separador()
    print(f"\n  TOP {TOP_PROCESOS} PROCESOS POR CPU\n")
    print(f"  {'PID':<8} {'NOMBRE':<30} {'CPU %':<10} {'RAM %'}")
    separador('─', 60)

    for p in top:
        # Truncar nombres muy largos
        nombre = p['nombre'][:28] if len(p['nombre']) > 28 else p['nombre']
        print(f"  {p['pid']:<8} {nombre:<30} {p['cpu']:<10.1f} {p['ram']:.1f}")


# ============================================================
#  FUNCIÓN PRINCIPAL
#  Muestra toda la información y se refresca cada N segundos
# ============================================================
def main():
    print("\n  Iniciando monitor... presiona Ctrl+C para salir.\n")
    time.sleep(1)

    # Ciclo infinito — igual que un while($true) en PowerShell
    while True:
        limpiar_pantalla()

        # Encabezado con fecha y hora actual
        ahora = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        print(f"\n  ╔══ MONITOR DE SISTEMA ══╗  {ahora}")

        # Llamamos a cada función de monitoreo
        mostrar_info_sistema()
        mostrar_cpu()
        mostrar_ram()
        mostrar_procesos()

        separador('═')
        print(f"  Actualizando en {INTERVALO_SEGUNDOS} segundos...  Ctrl+C para salir")
        separador('═')

        # Esperar antes de refrescar (igual que Start-Sleep en PowerShell)
        time.sleep(INTERVALO_SEGUNDOS)


# ============================================================
#  PUNTO DE ENTRADA
#  Solo se ejecuta si corres: python monitor.py
# ============================================================
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Capturamos Ctrl+C para salir limpiamente
        print("\n\n  Monitor detenido. ¡Hasta luego!\n")