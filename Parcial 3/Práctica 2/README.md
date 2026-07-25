# Práctica 2 Parcial 3

## Consumo de APIs REST con Postman y autenticación mediante API Key

En esta práctica se interactúa con la API pública de **ReqRes** para realizar operaciones CRUD. El trabajo se divide en dos fases:

* **Fase 1:** utilización de Postman para ejecutar y comprobar las peticiones de manera gráfica.
* **Fase 2:** desarrollo de un cliente en Python que automatiza las mismas solicitudes utilizando la biblioteca `requests` y una API Key almacenada en un archivo `.env`.

---

# Estructura del proyecto

```text
practica2-postman-auth/
├── usuarios_api.py
├── .env
├── .env.example
├── .gitignore
├── capturas/
│   └── .gitkeep
└── README.md
```

> El archivo `.env` contiene información de configuración local y no debe subirse al repositorio. En su lugar, se incluye `.env.example` como plantilla.

---

# Parte I: Uso de Postman

## Crear una colección

Dentro de Postman crea una nueva colección siguiendo estos pasos:

1. Haz clic en **New → Collection**.
2. Asigna el nombre **Practica2-ReqRes**.
3. Accede a la pestaña **Authorization**.
4. Selecciona **API Key** como método de autenticación.
5. Configura los siguientes valores:

```text
Key: x-api-key
Value: reqres-free-v1
Add to: Header
```

De esta forma todas las solicitudes de la colección enviarán automáticamente la clave de autenticación.

---

## Configurar un Environment

Crea un entorno llamado **ReqRes-Env** e incorpora la siguiente variable:

| Variable   | Valor                   |
| ---------- | ----------------------- |
| `base_url` | `https://reqres.in/api` |

Antes de comenzar las pruebas, asegúrate de seleccionar este entorno como activo.

---

## Crear las solicitudes

### Obtener usuarios

```text
Método: GET
URL: {{base_url}}/users?page=1
```

Respuesta esperada:

```text
200 OK
```

---

### Registrar un usuario

```text
Método: POST
URL: {{base_url}}/users
```

En **Body → raw → JSON** utiliza el siguiente contenido:

```json
{
  "name": "Ana Torres",
  "job": "Network Engineer"
}
```

Respuesta esperada:

```text
201 Created
```

---

### Modificar un usuario

```text
Método: PUT
URL: {{base_url}}/users/2
```

Body:

```json
{
  "name": "Ana Torres",
  "job": "Senior NE"
}
```

Respuesta esperada:

```text
200 OK
```

---

### Eliminar un usuario

```text
Método: DELETE
URL: {{base_url}}/users/2
```

Respuesta esperada:

```text
204 No Content
```

---

## Capturas solicitadas

Guarda las evidencias obtenidas durante las pruebas dentro del directorio `capturas/` utilizando nombres descriptivos, por ejemplo:

```text
01-get-usuarios.png
02-post-usuario.png
03-put-usuario.png
04-delete-usuario.png
05-sin-api-key.png
```

La última imagen debe mostrar el resultado de ejecutar una petición sin incluir el encabezado `x-api-key`, tal como lo solicita el checklist de la práctica.

---

## Si la API Key deja de funcionar

La documentación de la actividad utiliza la clave pública `reqres-free-v1`. Si el servicio responde con códigos **401** o **403**, genera una nueva API Key gratuita desde el sitio de ReqRes y actualiza ese valor tanto en Postman como en el archivo `.env`.

Evita escribir la clave directamente dentro del código fuente de `usuarios_api.py`.

---

# Parte II: Cliente en Python

## Abrir el proyecto

Carga la carpeta del proyecto en Visual Studio Code:

```text
practica2-postman-auth
```

---

## Crear el entorno virtual

En PowerShell ejecuta:

```powershell
python -m venv .venv
```

Después actívalo mediante:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si la política de ejecución de PowerShell impide la activación, puedes utilizar la consola CMD:

```bat
.venv\Scripts\activate.bat
```

---

## Instalar las librerías necesarias

```powershell
python -m pip install requests python-dotenv
```

---

## Configurar el archivo `.env`

Verifica que el archivo contenga la siguiente información:

```env
API_KEY=reqres-free-v1
BASE_URL=https://reqres.in/api
```

---

## Ejecutar el programa

Con el entorno virtual activo ejecuta:

```powershell
python usuarios_api.py
```

El script realiza automáticamente las siguientes solicitudes:

1. Consulta la primera página de usuarios.
2. Crea un nuevo usuario.
3. Actualiza el usuario con ID 2.
4. Elimina el usuario con ID 2.

---

## Resultados esperados

| Operación | Código HTTP esperado |
| --------- | :------------------: |
| GET       |          200         |
| POST      |          201         |
| PUT       |          200         |
| DELETE    |          204         |

Durante la ejecución se mostrarán en pantalla los datos obtenidos de cada operación y, al finalizar la eliminación, aparecerá una respuesta similar a:

```json
{
  "ok": true
}
```

---

# Respuestas al checklist

## ¿Qué código devuelve `GET /users`?

Cuando la solicitud incluye una API Key válida, el servidor responde con **200 OK**.

---

## ¿Cuál es la respuesta de `POST /users`?

La creación del usuario devuelve el código **201 Created**, indicando que la operación fue procesada correctamente.

---

## ¿Qué ocurre si no se envía `x-api-key`?

La API rechaza la solicitud y normalmente responde con **401 Unauthorized** o **403 Forbidden**, dependiendo de la validación aplicada por el servicio.

---

## ¿Qué utilidad tienen las variables de entorno en Postman?

Permiten almacenar datos reutilizables, como la URL base o una API Key, evitando repetir esos valores en cada solicitud y facilitando el cambio entre distintos entornos de trabajo.

---

## ¿Qué devuelve `os.getenv("API_KEY")` cuando no existe el archivo `.env`?

En ese caso el resultado será `None`, siempre que la variable no exista previamente como variable de entorno del sistema operativo. El programa valida esta situación para informar el problema al usuario.

---

## ¿Por qué utilizar `params=` para enviar parámetros?

El argumento `params` permite que la biblioteca `requests` genere automáticamente la cadena de consulta correspondiente.

Por ejemplo:

```python
params={"page": 1}
```

produce una petición equivalente a:

```text
https://reqres.in/api/users?page=1
```

Además, facilita agregar o modificar parámetros sin construir manualmente la URL.

---

## ¿Existe alguna diferencia entre realizar las pruebas con Postman y con Python?

En esencia no. Ambos métodos envían las mismas solicitudes HTTP utilizando los mismos endpoints, encabezados y cuerpos JSON. La diferencia es que Postman ofrece una interfaz gráfica para probar la API, mientras que Python permite automatizar todo el proceso mediante código.
