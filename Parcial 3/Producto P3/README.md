# MySteamInsight

Portal web construido con Flask que se conecta a tu cuenta de **Steam**
para mostrar tu perfil, tu biblioteca de juegos, tu actividad reciente,
un buscador del catálogo de la tienda y exportación de datos en CSV.

## Estructura del proyecto

```
MySteamInsight/
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── buscar.html
├── .env.example
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

## Requisitos previos

1. Una cuenta de Steam.
2. Una **API key** de Steam: https://steamcommunity.com/dev/apikey
   (pide un nombre de dominio; puedes usar `localhost` para pruebas).
3. Tu perfil de Steam (y, opcionalmente, tu biblioteca de juegos y tu
   lista de amigos) configurados como **públicos** en
   `Editar perfil > Privacidad`, para que la app pueda leer tus datos.
4. Python 3.10 o superior.

## Instalación

```bash
git clone <tu-repositorio>
cd MySteamInsight

python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Configuración

1. Copia el archivo de ejemplo:

   ```bash
   cp .env.example .env
   ```

2. Completa las variables en `.env`:

   | Variable            | Descripción                                                        |
   |---------------------|---------------------------------------------------------------------|
   | `FLASK_SECRET_KEY`  | Cadena aleatoria usada para firmar la sesión de Flask.              |
   | `STEAM_API_KEY`     | Tu API key de https://steamcommunity.com/dev/apikey                 |
   | `STEAM_REALM`       | Dominio autorizado, ej. `http://localhost:5000/`                    |
   | `STEAM_RETURN_URL`  | URL de callback, ej. `http://localhost:5000/callback`               |

## Ejecución

```bash
python app.py
```

La aplicación quedará disponible en `http://127.0.0.1:5000`.

## Funcionalidades

- **Login con Steam** mediante OpenID 2.0 (`/login`, `/callback`).
- **Panel (`/dashboard`)**: perfil, número de amigos, total de juegos,
  horas jugadas totales, juego más jugado, juegos nunca iniciados,
  top de juegos por horas y actividad de las últimas dos semanas.
- **Buscador (`/buscar`)**: búsqueda de juegos en la tienda de Steam
  (usa el endpoint público `storesearch` de Steam).
- **Exportación (`/exportar/biblioteca.csv`)**: descarga tu biblioteca
  completa ordenada por horas jugadas, en un CSV compatible con Excel.
- **Cierre de sesión (`/logout`)**: borra los datos locales de sesión.

## Notas y limitaciones

- Si tu perfil, biblioteca o lista de amigos son **privados**, Steam
  devolverá listas vacías para esos datos; la app seguirá funcionando
  pero mostrará estadísticas en cero.
- El endpoint de búsqueda de la tienda (`storesearch`) es un endpoint
  público no documentado oficialmente por Valve; su formato podría
  cambiar sin previo aviso.
- Este proyecto no está afiliado ni respaldado por Valve ni por Steam.

## Licencia

Uso educativo / personal.
