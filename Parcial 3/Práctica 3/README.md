# Práctica 3 Parcial 3

## Análisis y diagnóstico de respuestas HTTP

El propósito de esta práctica es enviar diversas solicitudes HTTP, identificar la categoría de cada respuesta según su código de estado, gestionar posibles errores de conexión y generar un reporte en formato JSON con el resultado de todas las pruebas realizadas.

El informe se guarda automáticamente en el archivo `diagnostico.json`.

---

# Instalación

## Dependencias

Desde una terminal ubicada en el directorio del proyecto ejecuta:

```powershell
python -m pip install -r requirements.txt
```

Si el archivo `requirements.txt` no está disponible, instala manualmente las bibliotecas necesarias:

```powershell
python -m pip install requests python-dotenv
```

---

# Ejecución del programa

Para iniciar las pruebas utiliza el siguiente comando:

```powershell
python diagnostico_api.py
```

Durante la ejecución se mostrará en la consola información sobre cada solicitud realizada, incluyendo:

* Método HTTP utilizado.
* URL consultada.
* Código de respuesta.
* Resultado obtenido.

Al finalizar, el programa creará (o actualizará si ya existe) el archivo:

```text
diagnostico.json
```

---

# Solicitudes incluidas

Las pruebas que realiza el script son las siguientes:

| Método | Recurso              | Código esperado |
| ------ | -------------------- | :-------------: |
| GET    | ReqRes `/users/1`    |       200       |
| GET    | ReqRes `/users/9999` |       404       |
| POST   | ReqRes `/users`      |       201       |
| DELETE | ReqRes `/users/2`    |       204       |
| GET    | `httpstat.us/500`    |       500       |
| GET    | `httpstat.us/401`    |       401       |

Los resultados pueden variar si alguno de los servicios externos no está disponible o si la API Key utilizada para ReqRes dejó de ser válida.

---

# Contenido del archivo `diagnostico.json`

El archivo generado resume todas las pruebas ejecutadas.

## `total_pruebas`

Indica la cantidad total de solicitudes realizadas por el programa.

---

## `exitosas`

Representa el número de respuestas cuyo código HTTP pertenece al rango **200–299**.

---

## `fallidas`

Incluye tanto las respuestas fuera del rango exitoso como los errores ocasionados por problemas de conexión, configuración o comunicación.

---

## `resultados`

Contiene una lista con la información detallada de cada solicitud ejecutada.

Cada elemento puede incluir los siguientes campos:

| Campo       | Descripción                                                          |
| ----------- | -------------------------------------------------------------------- |
| `url`       | Dirección a la que se envió la petición                              |
| `metodo`    | Método HTTP utilizado                                                |
| `status`    | Código de estado recibido                                            |
| `categoria` | Grupo al que pertenece el código HTTP                                |
| `tipo`      | Descripción del resultado                                            |
| `accion`    | Recomendación para interpretar o resolver el problema                |
| `exitoso`   | Valor booleano que indica si la respuesta pertenece a la familia 2xx |
| `error`     | Tipo de excepción cuando no fue posible obtener respuesta            |
| `detalle`   | Información adicional relacionada con el error                       |

---

# Clasificación de códigos HTTP

Las respuestas se agrupan según la familia del código de estado:

| Categoría | Significado                                  |
| --------- | -------------------------------------------- |
| 1xx       | Información                                  |
| 2xx       | Operación completada correctamente           |
| 3xx       | Redirección                                  |
| 4xx       | Error provocado por la solicitud del cliente |
| 5xx       | Error interno del servidor                   |

Para que las respuestas de tipo **3xx** puedan analizarse directamente, el programa utiliza `allow_redirects=False`, evitando que la biblioteca siga automáticamente la redirección.

---

# Respuestas al checklist

## ¿Por qué capturar `ConnectionError` y `Timeout` de manera independiente?

Aunque ambas excepciones representan fallos de comunicación, corresponden a situaciones distintas.

* **Timeout:** el servidor no respondió dentro del tiempo máximo establecido.
* **ConnectionError:** la conexión nunca pudo establecerse, ya sea por un problema de red, una URL inválida, un error DNS o porque el servidor no está disponible.

Manejar cada caso por separado permite generar diagnósticos más precisos.

---

## ¿Qué sucede al utilizar una URL inexistente?

Puedes añadir una prueba como la siguiente:

```python
{"metodo": "GET", "url": "https://url-que-no-existe.xyz"},
```

En la mayoría de los casos se producirá una excepción `requests.exceptions.ConnectionError`, registrando un resultado similar a:

```json
{
  "error": "Sin conexión",
  "accion": "Verificar red y URL",
  "exitoso": false
}
```

Dependiendo de la configuración de la red o del uso de un proxy, el comportamiento podría variar ligeramente.

---

## ¿Cómo verificar el código HTTP 429?

Añade esta entrada a la lista de pruebas:

```python
{"metodo": "GET", "url": "https://httpstat.us/429"},
```

El servicio `httpstat.us` responde utilizando el código especificado al final de la URL.

El diagnóstico esperado será similar a:

```json
{
  "status": 429,
  "categoria": "4xx",
  "tipo": "Too Many Requests",
  "accion": "Esperar antes de reintentar (rate limit)",
  "exitoso": false
}
```

---

# Solución de problemas

## Todas las solicitudes a ReqRes responden con 401

Comprueba que el archivo `.env` contenga una API Key válida.

```env
API_KEY=TU_CLAVE_REAL_DE_REQRES
```

Debe ser la misma utilizada previamente durante la práctica realizada con Postman.

---

## Aparece `ModuleNotFoundError`

Este error indica que alguna dependencia no está instalada.

Ejecuta nuevamente:

```powershell
python -m pip install requests python-dotenv
```

---

## No es posible acceder a `httpstat.us`

En ocasiones el servicio puede encontrarse temporalmente fuera de línea o bloqueado por la red utilizada.

Si esto ocurre, conserva las pruebas originales y vuelve a intentarlo más tarde. Mientras tanto, puedes utilizar temporalmente los siguientes recursos para comprobar el funcionamiento del clasificador de códigos HTTP:

```text
https://httpbin.org/status/500
https://httpbin.org/status/401
https://httpbin.org/status/429
```
