import csv
import io
import os
import re
import time
from collections import Counter
from datetime import datetime
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_session import Session

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Carpeta donde Flask guardará las sesiones
CARPETA_SESIONES = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".flask_session",
)

os.makedirs(CARPETA_SESIONES, exist_ok=True)

app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY"),
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=CARPETA_SESIONES,
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

Session(app)


# Credenciales de Steam
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_REALM = os.getenv("STEAM_REALM")
STEAM_RETURN_URL = os.getenv("STEAM_RETURN_URL")


# URLs oficiales de Steam
# Steam no usa OAuth2 como Spotify: la identidad se valida mediante
# OpenID 2.0, y los datos se consultan después con una API key propia.
OPENID_URL = "https://steamcommunity.com/openid/login"
API_BASE = "https://api.steampowered.com"
STORE_SEARCH_URL = "https://store.steampowered.com/api/storesearch"


# Expresión regular para extraer el SteamID64 del "claimed_id"
PATRON_STEAMID = re.compile(
    r"^https://steamcommunity\.com/openid/id/(\d+)$"
)


def construir_url_login():
    """
    Construye la URL de autenticación OpenID de Steam a la que
    se redirige al usuario para iniciar sesión.
    """
    parametros = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": STEAM_RETURN_URL,
        "openid.realm": STEAM_REALM,
        "openid.identity": (
            "http://specs.openid.net/auth/2.0/identifier_select"
        ),
        "openid.claimed_id": (
            "http://specs.openid.net/auth/2.0/identifier_select"
        ),
    }

    return f"{OPENID_URL}?{urlencode(parametros)}"


def verificar_respuesta_openid(argumentos):
    """
    Reenvía la respuesta recibida a los servidores de Steam para
    confirmar que la autenticación es legítima (protege contra
    respuestas falsificadas).
    """
    parametros = dict(argumentos)
    parametros["openid.mode"] = "check_authentication"

    respuesta = requests.post(
        OPENID_URL,
        data=parametros,
        timeout=15,
    )

    return "is_valid:true" in respuesta.text


def extraer_steamid(claimed_id):
    """
    Obtiene el SteamID64 a partir de la URL 'claimed_id' que
    Steam devuelve tras una autenticación exitosa.
    """
    if not claimed_id:
        return None

    coincidencia = PATRON_STEAMID.match(claimed_id)

    return coincidencia.group(1) if coincidencia else None


def guardar_sesion(steamid):
    """
    Guarda el SteamID del usuario dentro de la sesión local.
    """
    session["steamid"] = steamid
    session["autenticado_en"] = int(time.time())


def obtener_steamid():
    """
    Devuelve el SteamID guardado en la sesión, si existe.
    """
    return session.get("steamid")


def steam_get(endpoint, params=None):
    """
    Realiza una petición GET autenticada (vía API key) a la
    Steam Web API.
    """
    if not STEAM_API_KEY:
        raise RuntimeError(
            "Falta configurar STEAM_API_KEY en el archivo .env."
        )

    parametros = {
        "key": STEAM_API_KEY,
        "format": "json",
    }
    parametros.update(params or {})

    respuesta = requests.get(
        f"{API_BASE}{endpoint}",
        params=parametros,
        timeout=15,
    )

    if respuesta.status_code != 200:
        raise RuntimeError(
            f"Steam respondió HTTP {respuesta.status_code}: "
            f"{respuesta.text[:200]}"
        )

    return respuesta.json()


def analizar_biblioteca(juegos, recientes):
    """
    Procesa la biblioteca de juegos y genera estadísticas propias.
    """
    if not juegos:
        return {
            "total_juegos": 0,
            "horas_totales": 0,
            "juego_mas_jugado": "Sin datos",
            "top_juegos_por_horas": [],
            "juegos_nunca_jugados": 0,
            "actividad_reciente": [],
        }

    total_minutos = sum(
        juego.get("playtime_forever", 0) for juego in juegos
    )

    nunca_jugados = sum(
        1
        for juego in juegos
        if juego.get("playtime_forever", 0) == 0
    )

    ordenados = sorted(
        juegos,
        key=lambda juego: juego.get("playtime_forever", 0),
        reverse=True,
    )

    juego_mas_jugado = (
        ordenados[0].get("name", "Sin datos")
        if ordenados
        else "Sin datos"
    )

    top_juegos_por_horas = [
        (
            juego.get("name", "Desconocido"),
            round(juego.get("playtime_forever", 0) / 60, 1),
        )
        for juego in ordenados[:8]
    ]

    actividad_reciente = [
        (
            juego.get("name", "Desconocido"),
            round(juego.get("playtime_2weeks", 0) / 60, 1),
        )
        for juego in recientes
    ]

    return {
        "total_juegos": len(juegos),
        "horas_totales": round(total_minutos / 60, 1),
        "juego_mas_jugado": juego_mas_jugado,
        "top_juegos_por_horas": top_juegos_por_horas,
        "juegos_nunca_jugados": nunca_jugados,
        "actividad_reciente": actividad_reciente,
    }


@app.get("/")
def inicio():
    """
    Página de bienvenida del portal.
    """
    return render_template(
        "index.html",
        conectado=bool(obtener_steamid()),
    )


@app.get("/login")
def login():
    """
    Redirige al usuario a la pantalla de autenticación de Steam.
    """
    if not STEAM_API_KEY or not STEAM_REALM or not STEAM_RETURN_URL:
        flash(
            "Faltan credenciales en el archivo .env.",
            "error",
        )
        return redirect(url_for("inicio"))

    return redirect(construir_url_login())


@app.get("/callback")
def callback():
    """
    Recibe la respuesta OpenID de Steam, la valida y guarda
    el SteamID del usuario en la sesión local.
    """
    argumentos = request.args.to_dict()

    if argumentos.get("openid.mode") != "id_res":
        flash(
            "Steam no autorizó el acceso al portal.",
            "error",
        )
        return redirect(url_for("inicio"))

    if not verificar_respuesta_openid(argumentos):
        flash(
            "La validación de seguridad OpenID no coincidió.",
            "error",
        )
        return redirect(url_for("inicio"))

    steamid = extraer_steamid(argumentos.get("openid.claimed_id"))

    if not steamid:
        flash(
            "No fue posible identificar tu cuenta de Steam.",
            "error",
        )
        return redirect(url_for("inicio"))

    guardar_sesion(steamid)

    return redirect(url_for("dashboard"))


@app.get("/dashboard")
def dashboard():
    """
    Recupera perfil, biblioteca de juegos y actividad reciente.
    """
    steamid = obtener_steamid()

    if not steamid:
        flash(
            "Primero debes iniciar sesión con Steam.",
            "warning",
        )
        return redirect(url_for("inicio"))

    try:
        resumen = steam_get(
            "/ISteamUser/GetPlayerSummaries/v2/",
            params={"steamids": steamid},
        )

        jugadores = resumen.get("response", {}).get("players", [])
        perfil = jugadores[0] if jugadores else {}

        biblioteca = steam_get(
            "/IPlayerService/GetOwnedGames/v1/",
            params={
                "steamid": steamid,
                "include_appinfo": 1,
                "include_played_free_games": 1,
            },
        )

        juegos = biblioteca.get("response", {}).get("games", [])

        recientes_datos = steam_get(
            "/IPlayerService/GetRecentlyPlayedGames/v1/",
            params={
                "steamid": steamid,
                "count": 10,
            },
        )

        recientes = recientes_datos.get("response", {}).get(
            "games", []
        )

        total_amigos = 0

        try:
            amigos_datos = steam_get(
                "/ISteamUser/GetFriendList/v1/",
                params={
                    "steamid": steamid,
                    "relationship": "friend",
                },
            )

            total_amigos = len(
                amigos_datos.get("friendslist", {}).get(
                    "friends", []
                )
            )

        except RuntimeError:
            # El listado de amigos puede ser privado; no es un
            # error fatal para el resto del panel.
            total_amigos = 0

        estadisticas = analizar_biblioteca(juegos, recientes)

        top_juegos = sorted(
            juegos,
            key=lambda juego: juego.get("playtime_forever", 0),
            reverse=True,
        )[:10]

        return render_template(
            "dashboard.html",
            perfil=perfil,
            top_juegos=top_juegos,
            recientes=recientes,
            total_amigos=total_amigos,
            estadisticas=estadisticas,
        )

    except requests.exceptions.RequestException as error:
        flash(
            f"Error de conexión con Steam: {error}",
            "error",
        )
        return redirect(url_for("inicio"))

    except RuntimeError as error:
        flash(str(error), "error")
        return redirect(url_for("inicio"))


@app.get("/buscar")
def buscar():
    """
    Busca juegos en la tienda de Steam.
    """
    if not obtener_steamid():
        flash(
            "Primero debes iniciar sesión con Steam.",
            "warning",
        )
        return redirect(url_for("inicio"))

    consulta = request.args.get("q", "").strip()

    juegos = []

    if consulta:
        try:
            respuesta = requests.get(
                STORE_SEARCH_URL,
                params={
                    "term": consulta,
                    "l": "spanish",
                    "cc": "us",
                },
                timeout=15,
            )

            if respuesta.status_code == 200:
                juegos = respuesta.json().get("items", [])
            else:
                flash(
                    "La tienda de Steam respondió con un error "
                    f"HTTP {respuesta.status_code}.",
                    "error",
                )

        except requests.exceptions.RequestException as error:
            flash(
                f"Error de conexión con Steam: {error}",
                "error",
            )

    return render_template(
        "buscar.html",
        consulta=consulta,
        juegos=juegos,
    )


@app.get("/exportar/biblioteca.csv")
def exportar_biblioteca():
    """
    Recupera la biblioteca de juegos y genera un archivo CSV
    descargable, ordenado por horas jugadas.
    """
    steamid = obtener_steamid()

    if not steamid:
        flash(
            "Primero debes iniciar sesión con Steam.",
            "warning",
        )
        return redirect(url_for("inicio"))

    try:
        biblioteca = steam_get(
            "/IPlayerService/GetOwnedGames/v1/",
            params={
                "steamid": steamid,
                "include_appinfo": 1,
                "include_played_free_games": 1,
            },
        )

        juegos = biblioteca.get("response", {}).get("games", [])

    except requests.exceptions.RequestException as error:
        flash(
            f"Error de conexión con Steam: {error}",
            "error",
        )
        return redirect(url_for("dashboard"))

    except RuntimeError as error:
        flash(str(error), "error")
        return redirect(url_for("dashboard"))

    juegos_ordenados = sorted(
        juegos,
        key=lambda juego: juego.get("playtime_forever", 0),
        reverse=True,
    )

    salida = io.StringIO()

    escritor = csv.writer(
        salida,
        lineterminator="\n",
    )

    escritor.writerow(
        [
            "posicion",
            "juego",
            "horas_totales",
            "horas_ultimas_2_semanas",
            "app_id",
        ]
    )

    for posicion, juego in enumerate(juegos_ordenados, start=1):
        escritor.writerow(
            [
                posicion,
                juego.get("name", ""),
                round(juego.get("playtime_forever", 0) / 60, 1),
                round(juego.get("playtime_2weeks", 0) / 60, 1),
                juego.get("appid", ""),
            ]
        )

    nombre_archivo = (
        "mysteaminsight_biblioteca_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    contenido = "\ufeff" + salida.getvalue()

    return Response(
        contenido,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{nombre_archivo}"'
            )
        },
    )


@app.get("/logout")
def logout():
    """
    Elimina los datos de sesión almacenados localmente.
    """
    session.clear()

    flash(
        "La sesión local fue cerrada correctamente.",
        "success",
    )

    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
