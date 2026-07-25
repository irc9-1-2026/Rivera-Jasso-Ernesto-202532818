# Práctica 1 Parcial 3

## Desarrollo y consumo de un servicio REST

Este proyecto implementa una API REST utilizando Python y está dividido en dos componentes principales:

* **Versión 1:** aplicación desarrollada con Flask que expone una API para administrar dispositivos de red.
* **Versión 2:** programa cliente escrito en Python que interactúa con la API mediante la librería `requests`.

La aplicación permite realizar operaciones de creación, consulta, actualización y eliminación (CRUD) sobre diferentes equipos de red, como routers, switches, firewalls y puntos de acceso.

---

## Organización del proyecto

```text
practica1-api-rest/
├── api_dispositivos.py
├── cliente.py
└── README.md
```

---

## Software necesario

Antes de comenzar, verifica que tengas instalado lo siguiente:

* Python 3.10 o una versión más reciente.
* Visual Studio Code.
* Git.
* Una cuenta en GitHub con un repositorio disponible.

---

## Configuración inicial

Abre la carpeta del proyecto desde Visual Studio Code y crea un entorno virtual para instalar las dependencias.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask requests
```

### Windows (Símbolo del sistema)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install flask requests
```

### Linux y macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask requests
```

---

# Ejecución de la API (Versión 1)

Desde una terminal ubicada en el directorio del proyecto ejecuta:

```bash
python api_dispositivos.py
```

Una vez iniciado el servidor, la API estará disponible en la siguiente dirección:

```text
http://localhost:5000
```

Mantén esta terminal abierta mientras realizas las pruebas o ejecutas el cliente.

## Recursos disponibles

| Método HTTP | Endpoint             | Función                             | Código esperado |
| ----------- | -------------------- | ----------------------------------- | :-------------: |
| GET         | `/dispositivos`      | Obtener todos los dispositivos      |       200       |
| GET         | `/dispositivos/<id>` | Consultar un dispositivo específico |    200 / 404    |
| POST        | `/dispositivos`      | Registrar un nuevo dispositivo      |       201       |
| PUT         | `/dispositivos/<id>` | Modificar un dispositivo existente  |    200 / 404    |
| DELETE      | `/dispositivos/<id>` | Eliminar un dispositivo             |    204 / 404    |

---

## Verificación desde el navegador

Puedes comprobar el funcionamiento de la API ingresando a:

```text
http://localhost:5000/dispositivos
```

También es posible consultar un identificador inexistente, por ejemplo:

```text
http://localhost:5000/dispositivos/99
```

En este caso la respuesta esperada será un error **404 (Not Found)** acompañado de un mensaje en formato JSON.

---

# Ejecución del cliente (Versión 2)

Con el servidor Flask funcionando, abre una segunda terminal y ejecuta:

```bash
python cliente.py
```

El cliente realiza automáticamente la siguiente secuencia de acciones:

1. Recupera la lista completa de dispositivos.
2. Consulta el dispositivo con ID **1**.
3. Registra un nuevo punto de acceso.
4. Actualiza la información del dispositivo con ID **2**.
5. Elimina el dispositivo con ID **3**.
6. Solicita nuevamente la lista para verificar los cambios realizados.

---

## Comportamiento esperado

Al ejecutar el cliente deberían obtenerse los siguientes resultados:

* La consulta general (`GET`) responde con **200 OK**.
* La creación del nuevo dispositivo (`POST`) devuelve **201 Created**.
* La actualización (`PUT`) responde con **200 OK**.
* La eliminación (`DELETE`) finaliza con **204 No Content**.
* La consulta final muestra el nuevo dispositivo agregado y confirma que el ID 3 ya no existe.

> La información únicamente permanece en memoria. Si el servidor Flask se reinicia, todos los cambios realizados durante la ejecución se perderán y se restaurará la lista original.

---

# Preguntas del checklist

## ¿Qué sucede al acceder a `/dispositivos/99`?

Como ese identificador no existe, la API devuelve un objeto JSON similar al siguiente:

```json
{
  "error": "Dispositivo no encontrado"
}
```

La respuesta utiliza el código HTTP **404 Not Found**.

---

## ¿Cuál es el propósito de `global dispositivos` dentro de `eliminar()`?

La función reemplaza la lista original por una nueva versión sin el elemento eliminado. Para que esa modificación afecte a la variable global utilizada por toda la aplicación es necesario declararla con `global`; de lo contrario, Python crearía una variable local independiente.

---

## ¿Qué inconveniente presenta utilizar una lista de Python como almacenamiento?

La información únicamente reside en memoria RAM. Esto significa que desaparece cuando la aplicación termina, no existe persistencia y el mecanismo no resulta adecuado para aplicaciones con múltiples usuarios o procesos simultáneos.

---

## ¿Por qué el dispositivo con ID 3 ya no aparece después del DELETE?

Porque la operación elimina ese registro de la colección de dispositivos. Cuando se realiza una nueva consulta (`GET`), la lista ya refleja dicha modificación.

---

## ¿Qué ocurre si el cliente intenta conectarse y el servidor está detenido?

La conexión no puede establecerse y la biblioteca `requests` normalmente genera una excepción del tipo:

```text
requests.exceptions.ConnectionError
```

---

## ¿Qué sucede si un POST recibe `json={}`?

Cuando el cuerpo de la petición está vacío, la API asigna automáticamente los siguientes valores por defecto:

```json
{
  "nombre": "Sin nombre",
  "tipo": "desconocido",
  "ip": "0.0.0.0",
  "estado": "activo"
}
```

El identificador del dispositivo se asigna de forma automática.

---

## ¿Qué información muestran los registros generados por Flask?

Los registros incluyen datos como la dirección IP del cliente, fecha y hora de la solicitud, método HTTP utilizado, recurso solicitado, versión del protocolo y código de respuesta. Si ocurre algún problema durante la ejecución, también se muestran los mensajes de error correspondientes.

---

# Publicación del proyecto en GitHub

Reemplaza la URL de ejemplo por la correspondiente a tu propio repositorio.

## Publicar la API en la rama principal

```bash
git init
git add api_dispositivos.py README.md
git commit -m "v1: API REST de dispositivos con Flask"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/practica1-api-rest.git
git push -u origin main
```

---

## Publicar el cliente en una rama independiente

```bash
git checkout -b feature/cliente-requests
git add cliente.py
git commit -m "v2: cliente Python para consumir la API"
git push -u origin feature/cliente-requests
```

---

## Fusionar ambas versiones

```bash
git checkout main
git merge feature/cliente-requests
git push origin main
```

---

# Observaciones

Con fines didácticos, la aplicación utiliza una lista de diccionarios como almacenamiento temporal de datos. Esto permite centrar la práctica en el funcionamiento de una API REST, el intercambio de información mediante HTTP y el uso de los métodos **GET**, **POST**, **PUT** y **DELETE**, sin depender todavía de un sistema de base de datos.
