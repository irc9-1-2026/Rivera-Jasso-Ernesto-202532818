# Práctica 4 Parcial 3

## Implementación de un Dashboard con CI/CD

Esta práctica integra una aplicación desarrollada con Flask que muestra el estado de varios servicios web. El dashboard obtiene información desde cuatro APIs públicas y una API local de dispositivos.

Además, el proyecto incorpora un flujo de integración y despliegue continuo (CI/CD) mediante GitHub Actions. Cuando las pruebas automatizadas finalizan correctamente, la aplicación puede desplegarse en un servidor Rocky Linux utilizando una conexión SSH.

---

# Ejecución en el equipo local

Antes de iniciar la aplicación instala las dependencias y ejecuta las pruebas:

```powershell id="jh7hpr"
python -m pip install -r requirements.txt
python -m unittest test_app.py -v
python app.py
```

Una vez iniciado el servidor, abre el navegador en:

```text id="z1zkam"
http://127.0.0.1:5000
```

---

# Configuración del entorno

Crea un archivo llamado `.env` en el directorio del proyecto con el siguiente contenido:

```env id="vr1a9n"
REQRES_API_KEY=TU_API_KEY_DE_REQRES
```

Este archivo contiene información privada de configuración, por lo que no debe agregarse al repositorio.

---

# Preparación del servidor Rocky Linux

Clona el repositorio completo en la siguiente ubicación:

```text id="3lsm0q"
/opt/dashboard
```

Después accede a la carpeta correspondiente a la práctica y crea un entorno virtual:

```bash id="7qv12o"
cd /opt/dashboard/Parcial-3/Practica-4
python3.11 -m venv venv
./venv/bin/pip install -r requirements.txt
```

---

# Configuración de los servicios

Copia los archivos de servicio de systemd y habilítalos para que inicien automáticamente:

```bash id="0vy4bk"
cp dashboard.service /etc/systemd/system/dashboard.service
cp api-dispositivos.service /etc/systemd/system/api-dispositivos.service
systemctl daemon-reload
systemctl enable --now dashboard api-dispositivos
```

---

# Configuración de Nginx

Instala la configuración del servidor web y habilita la comunicación con la aplicación Flask:

```bash id="djlwm2"
cp nginx-dashboard.conf /etc/nginx/conf.d/dashboard.conf
setsebool -P httpd_can_network_connect 1
nginx -t
systemctl restart nginx
```

---

# Verificación de funcionamiento

Comprueba que tanto el dashboard como la API local respondan correctamente ejecutando:

```bash id="3fxv8z"
curl http://127.0.0.1:5000/api/estado
curl http://127.0.0.1:5001/dispositivos
```

Si ambas solicitudes devuelven una respuesta válida, la configuración del servidor será correcta.

---

# Secrets necesarios en GitHub

Para permitir que GitHub Actions establezca la conexión SSH con el servidor, configura los siguientes Secrets en el repositorio:

* `SSH_PRIVATE_KEY`
* `SERVER_HOST`
* `SERVER_USER`
* `SERVER_PORT`

Los valores utilizados para esta práctica son:

* `SERVER_USER = deploy`
* `SERVER_PORT = 22`

Ten presente que una dirección privada como `192.168.100.17` únicamente es accesible desde la red local. Los runners administrados por GitHub no pueden conectarse directamente a direcciones IP privadas, por lo que será necesario habilitar un mecanismo de acceso seguro antes de utilizar el despliegue automático.

---

# Habilitar el proceso de despliegue

Mientras el servidor permanezca accesible únicamente mediante una red privada de VirtualBox, el flujo de **deploy** permanecerá deshabilitado utilizando la variable `ENABLE_DEPLOY`.

Cuando exista conectividad segura entre GitHub Actions y el servidor Rocky Linux, crea la siguiente variable dentro del repositorio:

```text id="j22fqc"
Settings → Secrets and variables → Actions → Variables
```

Agrega la variable:

```text id="i88c0e"
ENABLE_DEPLOY=true
```

Antes de habilitar esta opción verifica que los cuatro Secrets de autenticación SSH ya se encuentren configurados; de lo contrario, el proceso de despliegue no podrá establecer conexión con el servidor remoto.
