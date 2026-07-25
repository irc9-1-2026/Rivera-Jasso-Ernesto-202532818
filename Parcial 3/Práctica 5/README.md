# Práctica 5 Parcial 3
## Deploy con Docker Compose y CI/CD

El dashboard de la Práctica 4 se ejecuta ahora dentro de contenedores. Docker
Compose construye y administra:

1. `flask-app`: dashboard Flask servido por Gunicorn.
2. `api-dispositivos`: API interna de la Práctica 1.
3. `nginx`: proxy inverso y único servicio publicado en el puerto 80.

El tercer servicio conserva la tarjeta **Mi API Local** y hace que toda la
solución sea portátil: el servidor solo necesita Docker.

## Estructura

```text
repo/
├── .github/
│   └── workflows/
│       └── deploy-docker.yml
└── Parcial-3/
    └── Practica-5/
        ├── nginx/
        │   └── nginx.conf
        ├── templates/
        │   └── index.html
        ├── app.py
        ├── api_dispositivos.py
        ├── test_app.py
        ├── Dockerfile
        ├── docker-compose.yml
        ├── requirements.txt
        ├── .dockerignore
        ├── .env.example
        ├── .gitignore
        └── README.md
```

## Diferencias respecto a la Práctica 4

### 1. Aislamiento

En la Práctica 4, Python, Gunicorn y Nginx dependían directamente de Rocky
Linux. En esta práctica cada servicio vive dentro de su propio contenedor y no
comparte sus dependencias con el sistema operativo.

### 2. Portabilidad

El proyecto puede ejecutarse igual en cualquier equipo con Docker Compose. No
es necesario reproducir manualmente la instalación de Python, librerías,
Gunicorn y archivos de Nginx.

### 3. Despliegue reproducible

El pipeline ya no reinicia servicios de systemd. Ejecuta:

```bash
docker compose up --build -d
```

Ese comando reconstruye las imágenes cuando cambia el código y deja los
contenedores ejecutándose en segundo plano.

### 4. Recuperación automática

`restart: always` permite que Docker vuelva a levantar los contenedores si
fallan o si el servidor se reinicia.

### 5. Exposición mínima

Flask no publica ningún puerto en el host. Nginx es el único servicio accesible
desde el exterior mediante el puerto 80.

---

# Respuestas del checklist

## ¿Por qué copiar `requirements.txt` primero?

Docker reutiliza las capas anteriores cuando no cambian. Si las dependencias
siguen iguales, no vuelve a ejecutar `pip install` cada vez que cambia
`app.py`, lo que acelera las reconstrucciones.

## `python:3.11` frente a `python:3.11-slim`

La variante `slim` elimina paquetes y utilidades del sistema que no son
necesarios para la mayoría de aplicaciones. Produce una imagen más pequeña,
aunque algunas dependencias que compilan código nativo podrían requerir
instalar paquetes adicionales.

## ¿Qué hace `EXPOSE 5000`?

Documenta que la aplicación escucha en el puerto 5000 dentro del contenedor.
No publica ese puerto en Internet. La publicación solo ocurre mediante
`ports:` en Docker Compose o `-p` en `docker run`.

## ¿Por qué Flask no publica puerto, pero Nginx puede acceder?

Los servicios comparten `red-interna`. Docker proporciona DNS interno y permite
que Nginx resuelva `flask-app` por su nombre de servicio y se conecte al puerto
5000 del contenedor. El host no puede acceder directamente porque no existe un
mapeo `ports` para Flask.

## ¿Qué hace `depends_on`?

Controla el orden de creación e inicio. Con la sintaxis corta utilizada, inicia
la dependencia antes, pero no garantiza que la aplicación ya esté preparada
para aceptar solicitudes. Nginx volverá a intentar las conexiones cuando Flask
termine de iniciar.

## ¿Qué ocurre con `restart: "no"`?

Docker no reinicia automáticamente el contenedor después de un fallo. El
servicio permanece detenido hasta que un administrador lo arranque.

## ¿Por qué `proxy_pass` usa `flask-app` en vez de una IP?

Los contenedores reciben direcciones dinámicas. Docker Compose registra los
nombres de los servicios en su DNS interno; `flask-app` sigue siendo estable
aunque el contenedor sea recreado con una IP diferente.

## ¿Qué reemplaza a `systemctl restart dashboard`?

```bash
docker compose up --build -d
```

Este comando construye imágenes nuevas, recrea los contenedores necesarios y
mantiene los servicios ejecutándose en segundo plano.

## ¿Por qué ejecutar `docker image prune -f`?

Las reconstrucciones pueden dejar imágenes antiguas sin etiqueta. La limpieza
evita que se acumulen y consuman espacio de disco con el tiempo.

---

# CI/CD

El workflow utiliza los mismos Secrets de la Práctica 4:

```text
SSH_PRIVATE_KEY
SERVER_HOST
SERVER_USER
SERVER_PORT
TAILSCALE_AUTHKEY
```

Flujo:

```text
push a main
→ pruebas unitarias
→ validación de Compose
→ build de Docker
→ conexión Tailscale
→ SSH a Rocky
→ git pull
→ docker compose up --build -d
→ verificación del proxy
```

`needs: test` impide ejecutar el deploy cuando falla una prueba.

---
