# Control de equipos tecnológicos

API REST para administrar los equipos tecnológicos y los usuarios de una organización.
Desarrollada con FastAPI, organizada por capas y conectada a una base de datos PostgreSQL en Neon.

**Ejercicio 10 · Aprendiz: Evelio Restrepo Marín**

---

## Contenido

1. [Tecnologías](#tecnologías)
2. [Arquitectura por capas](#arquitectura-por-capas)
3. [Modelo de datos](#modelo-de-datos)
4. [Endpoints](#endpoints)
5. [Instalación en Windows](#instalación-en-windows)
6. [Variables de entorno](#variables-de-entorno)
7. [Base de datos en Neon](#base-de-datos-en-neon)
8. [Ejecución y documentación interactiva](#ejecución-y-documentación-interactiva)
9. [Pruebas desde PowerShell](#pruebas-desde-powershell)
10. [Despliegue en Render](#despliegue-en-render)
11. [Solución de problemas](#solución-de-problemas)

---

## Tecnologías

| Herramienta | Para qué se usa |
|---|---|
| FastAPI | Framework de la API |
| Uvicorn | Servidor que ejecuta la API |
| SQLAlchemy | ORM: las tablas como clases de Python |
| psycopg2-binary | Driver para conectarse a PostgreSQL |
| python-dotenv | Lee la configuración desde el archivo `.env` |
| Neon | Base de datos PostgreSQL en la nube |
| Render | Plataforma donde se despliega la API |

Pydantic, que valida los datos de entrada y salida, viene incluido con FastAPI.

---

## Arquitectura por capas

Cada capa tiene una responsabilidad. Así el código es más fácil de leer, probar y cambiar.

```
Control-de-equipos/
├── main.py                # Punto de entrada: expone la app para Uvicorn
├── app/
│   ├── main.py            # Crea la aplicación FastAPI y registra routers y manejadores de errores
│   ├── database.py        # Conexión a Neon, sesión y clase base de los modelos
│   ├── api/
│   │   ├── equipos.py     # Rutas HTTP de equipos
│   │   └── usuarios.py    # Rutas HTTP de usuarios
│   └── services/
│       └── errors.py      # Errores de negocio (NotFoundError, ConflictError)
├── requirements.txt       # Librerías necesarias
├── render.yaml            # Configuración de despliegue en Render
├── .python-version        # Versión de Python para Render
├── .env.example           # Plantilla de configuración (sin datos reales)
├── .gitignore             # Archivos que Git no sube
└── README.md
```

| Capa | Responsabilidad |
|---|---|
| Entrada (`main.py`) | Es lo que Uvicorn ejecuta: `uvicorn main:app` |
| Aplicación (`app/main.py`) | Crea la app, crea las tablas al arrancar y traduce los errores de negocio a respuestas 404 y 409 |
| API (`app/api/`) | Recibe las peticiones HTTP, valida los datos y responde |
| Servicios (`app/services/`) | Reglas de negocio y errores propios |
| Datos (`app/database.py`) | Conexión con Neon y sesión de base de datos por petición |

---

## Modelo de datos

### Equipos

| Campo | Tipo | Notas |
|---|---|---|
| `id` | entero | Autoincremental |
| `nombre` | texto (100) | Obligatorio |
| `codigo_inventario` | texto (50) | Obligatorio y único |
| `marca` | texto (50) | Obligatorio |
| `modelo` | texto (50) | Obligatorio |
| `fecha_adquisicion` | fecha | Formato `AAAA-MM-DD` |

### Usuarios

| Campo | Tipo | Notas |
|---|---|---|
| `id` | entero | Autoincremental |
| `nombre` | texto (100) | Obligatorio |
| `correo` | texto (120) | Obligatorio, único, con formato `algo@dominio.ext`; se guarda en minúsculas |
| `cargo` | texto (80) | Obligatorio |

---

## Endpoints

### Equipos

| Actividad | Método | Ruta |
|---|---|---|
| Registrar equipos | POST | `/equipos` |
| Consultar todos los equipos | GET | `/equipos` |
| Consultar un equipo por ID | GET | `/equipos/{id}` |
| Actualizar la información de un equipo | PUT | `/equipos/{id}` |
| Filtrar equipos por marca | GET | `/equipos?marca=Dell` |
| Eliminar equipos | DELETE | `/equipos/{id}` |

**Filtro por marca.** Es un parámetro opcional (`marca`) de `GET /equipos`.
No distingue mayúsculas: `Dell`, `dell` y `DELL` devuelven lo mismo.
Si no se envía, se devuelven todos los equipos.

Ejemplo de cuerpo para registrar o actualizar un equipo:

```json
{
  "nombre": "Portátil Gerencia",
  "codigo_inventario": "INV-001",
  "marca": "Dell",
  "modelo": "Latitude 5420",
  "fecha_adquisicion": "2025-03-15"
}
```

### Usuarios

| Acción | Método | Ruta |
|---|---|---|
| Registrar usuario | POST | `/usuarios` |
| Consultar todos | GET | `/usuarios` |
| Consultar por ID | GET | `/usuarios/{id}` |
| Actualizar usuario | PUT | `/usuarios/{id}` |
| Eliminar usuario | DELETE | `/usuarios/{id}` |

Ejemplo de cuerpo para registrar o actualizar un usuario:

```json
{
  "nombre": "Ana Pérez",
  "correo": "ana@empresa.com",
  "cargo": "Soporte"
}
```

### Códigos de respuesta

| Código | Significado |
|---|---|
| 200 | Consulta o actualización correcta |
| 201 | Registro creado |
| 204 | Registro eliminado |
| 404 | El registro no existe |
| 409 | Dato duplicado (código de inventario o correo ya en uso) |
| 422 | Datos inválidos (campo vacío, fecha o correo mal escritos) |

---

## Instalación en Windows

Requisito: tener Python instalado (en el instalador, marcar **Add python.exe to PATH**).

1. Clonar el repositorio y entrar a la carpeta:
   ```
   git clone <URL-del-repositorio>
   cd Control-de-equipos
   ```
2. Crear y activar el entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   Si PowerShell bloquea el `activate`, ejecutar una vez
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y repetir.
3. Instalar las librerías:
   ```
   pip install -r requirements.txt
   ```
4. Crear el archivo `.env` (ver la siguiente sección).

---

## Variables de entorno

La API lee la conexión a la base de datos desde la variable `DATABASE_URL`.

1. Copiar la plantilla:
   ```
   copy .env.example .env
   ```
2. En Neon, abrir el proyecto, pulsar **Connect** y copiar la *connection string*.
3. Pegarla en el `.env`, en una sola línea, **cambiando el inicio a `postgresql+psycopg2://`**:
   ```
   DATABASE_URL=postgresql+psycopg2://USUARIO:CLAVE@HOST/NOMBRE_BD?sslmode=require
   ```

Notas importantes:

- El archivo `.env` contiene la contraseña real y **no se sube a GitHub** (está en `.gitignore`).
- `.env.example` es solo una plantilla con datos falsos y sí se sube.
- Sin comillas ni espacios alrededor del `=`.
- Si la contraseña se expone, restablecerla en Neon (**Roles → Reset password**) y actualizar el `.env` y la variable de Render.

---

## Base de datos en Neon

La API crea las tablas automáticamente al arrancar. También pueden crearse a mano en el **SQL Editor** de Neon:

```sql
CREATE TABLE IF NOT EXISTS equipos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_inventario VARCHAR(50) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    fecha_adquisicion DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_equipos_marca ON equipos (marca);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    cargo VARCHAR(80) NOT NULL
);
```

Para comprobar que los datos llegan a Neon:

```sql
SELECT * FROM equipos;
SELECT * FROM usuarios;
```

---

## Ejecución y documentación interactiva

Con el entorno virtual activo y desde la raíz del proyecto:

```
python -m uvicorn main:app --reload
```

Cuando aparezca `Application startup complete.`, abrir:

| Dirección | Qué muestra |
|---|---|
| `http://127.0.0.1:8000/docs` | Documentación interactiva (Swagger): permite probar todo el CRUD |
| `http://127.0.0.1:8000/redoc` | Documentación alternativa |

En `/docs`, pulsar **Try it out** en un endpoint, completar los datos y pulsar **Execute**.

Para usar otro puerto: `python -m uvicorn main:app --reload --port 8001`.
La terminal donde corre el servidor debe quedar abierta. Para detenerlo, `Ctrl+C`.

---

## Pruebas desde PowerShell

Con el servidor corriendo en una terminal, usar **otra** terminal de PowerShell:

```powershell
# Registrar un usuario
Invoke-RestMethod -Uri "http://127.0.0.1:8000/usuarios" -Method Post -ContentType "application/json" -Body '{"nombre":"Ana Perez","correo":"ana@empresa.com","cargo":"Soporte"}'

# Consultar todos
Invoke-RestMethod -Uri "http://127.0.0.1:8000/usuarios"

# Consultar por ID
Invoke-RestMethod -Uri "http://127.0.0.1:8000/usuarios/1"

# Actualizar
Invoke-RestMethod -Uri "http://127.0.0.1:8000/usuarios/1" -Method Put -ContentType "application/json" -Body '{"nombre":"Ana Perez","correo":"ana@empresa.com","cargo":"Jefe de soporte"}'

# Eliminar
Invoke-RestMethod -Uri "http://127.0.0.1:8000/usuarios/1" -Method Delete

# Filtrar equipos por marca
Invoke-RestMethod -Uri "http://127.0.0.1:8000/equipos?marca=Dell"
```

`Invoke-RestMethod` solo existe en PowerShell. En CMD se puede usar `curl`.

---

## Despliegue en Render

1. Subir el proyecto a GitHub (sin `.env`, `venv`, `.venv` ni archivos `.db`).
2. En Render: **New → Web Service** y conectar el repositorio.
3. Configuración:

   | Campo | Valor |
   |---|---|
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Plan | Free |

4. En **Environment**, agregar la variable `DATABASE_URL` con la conexión de Neon
   (valor completo, empezando con `postgresql+psycopg2://`, sin `DATABASE_URL=` delante).
5. Pulsar **Deploy**. Cuando el estado sea **Live**, abrir `https://TU-SERVICIO.onrender.com/docs`.

El archivo `render.yaml` ya trae esta configuración, y `.python-version` fija la versión de Python.
En el plan gratuito el servicio se duerme tras unos 15 minutos sin uso; la primera visita después tarda cerca de un minuto.

---

## Solución de problemas

| Síntoma | Causa y solución |
|---|---|
| `uvicorn` no se reconoce como comando | El entorno virtual no está activo o no tiene las librerías. Activar con `venv\Scripts\activate`, ejecutar `pip install -r requirements.txt` y arrancar con `python -m uvicorn main:app --reload` |
| `Python was not found` | Python no está instalado o no está en el PATH. Instalarlo marcando **Add python.exe to PATH**, o probar `py -m venv venv` |
| `Falta DATABASE_URL en el archivo .env` | No existe el `.env` o no está en la raíz. En Render, falta la variable en **Environment** |
| `No module named 'psycopg'` | La URL empieza con `postgresql://`. Cambiarla a `postgresql+psycopg2://` |
| `could not translate host name "HOST"` | El `.env` aún tiene los datos de ejemplo. Pegar la conexión real de Neon |
| `Could not parse SQLAlchemy URL` | La URL está mal escrita (por ejemplo, `postgresql:postgresql://`). Debe quedar `postgresql+psycopg2://...` |
| `ERR_CONNECTION_REFUSED` o `No es posible conectar con el servidor remoto` | El servidor no está corriendo o usa otro puerto. Arrancarlo y usar el mismo puerto en la URL |
| `Invoke-RestMethod` no se reconoce | La terminal es CMD. Escribir `powershell` o usar `curl` |
| `/docs` responde 404 | La documentación está desactivada (`docs_url=None`) en `app/main.py`, o hay otro servidor en el mismo puerto |
| Cambió el `.env` y no se nota | `--reload` solo vigila archivos `.py`. Reiniciar el servidor con `Ctrl+C` y volver a arrancarlo |

Para ver a qué base se conecta la API, sin mostrar la contraseña:

```
python -c "from app.database import engine; print(engine.dialect.name, engine.url.host, engine.url.database)"
```

Debe mostrar `postgresql ep-...neon.tech neondb`.

---

Ejercicio 10 · Evelio Restrepo Marín
