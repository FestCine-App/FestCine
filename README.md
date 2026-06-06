# 🎬 FestCine — Sistema de Gestión de Festival de Cine Independiente

Sistema de gestión completo para el Festival Internacional de Cine Independiente **FestCine**. Incluye base de datos relacional en PostgreSQL, backend API en Django (Python) y frontend en React.

---

## 📋 Índice

1. [Tecnologías utilizadas](#tecnologías-utilizadas)
2. [Requisitos previos](#requisitos-previos)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Instalación paso a paso](#instalación-paso-a-paso)
   - [Paso 1 — Clonar el repositorio](#paso-1--clonar-el-repositorio)
   - [Paso 2 — Crear y cargar la base de datos](#paso-2--crear-y-cargar-la-base-de-datos)
   - [Paso 3 — Configurar el backend](#paso-3--configurar-el-backend)
   - [Paso 4 — Configurar el frontend](#paso-4--configurar-el-frontend)
   - [Paso 5 — Verificar que todo funciona](#paso-5--verificar-que-todo-funciona)
5. [Flujos críticos a probar](#flujos-críticos-a-probar)
6. [Solución de problemas comunes](#solución-de-problemas-comunes)

---

## Tecnologías utilizadas

| Capa | Tecnología | Versión recomendada |
|---|---|---|
| Base de datos | PostgreSQL | 13 o superior |
| Backend | Python + Django | Python 3.11+, Django 5.x |
| Frontend | React + Vite | Node.js 18+ |
| Conector BD | pg8000 | incluido en requirements.txt |

---

## Requisitos previos

Antes de comenzar, asegúrate de tener instalado en tu computadora:

### 1. PostgreSQL
- Descargar desde: https://www.postgresql.org/download/
- Durante la instalación, recordar la **contraseña** que le asignes al usuario `postgres` — la necesitarás más adelante.
- Verificar que está instalado correctamente abriendo una terminal y ejecutando:
  ```
  psql --version
  ```
  Debe mostrar algo como: `psql (PostgreSQL) 15.x`

> **Windows:** Si el comando `psql` no es reconocido, debes agregar PostgreSQL al PATH del sistema. La ruta típica es `C:\Program Files\PostgreSQL\15\bin`. Busca "Variables de entorno" en el Panel de Control → Configuración avanzada del sistema → Variables de entorno → Path → Editar → Nuevo → pegar la ruta.

### 2. Python 3.11 o superior
- Descargar desde: https://www.python.org/downloads/
- **Importante durante la instalación en Windows:** marcar la casilla **"Add Python to PATH"**.
- Verificar:
  ```
  python --version
  ```
  Debe mostrar: `Python 3.11.x` o superior.

### 3. Node.js 18 o superior
- Descargar desde: https://nodejs.org/ (elegir la versión LTS)
- Verificar:
  ```
  node --version
  npm --version
  ```

### 4. Git
- Descargar desde: https://git-scm.com/downloads
- Verificar:
  ```
  git --version
  ```

---

## Estructura del proyecto

```
FestCine/
├── database/
│   └── festcinedb.sql        # Script completo: tablas, datos, procedimientos, triggers
├── backend/                  # API Django (Python)
│   ├── api/
│   │   ├── views.py          # Endpoints REST
│   │   └── urls.py           # Rutas de la API
│   ├── config/
│   │   └── database.py       # Conexión a PostgreSQL + wrappers de procedimientos
│   ├── festcine_backend/
│   │   └── settings.py       # Configuración de Django
│   ├── manage.py
│   └── requirements.txt      # Dependencias Python
├── frontend/                 # App React (Vite)
│   ├── src/
│   │   ├── pages/            # Páginas de la aplicación
│   │   └── api/index.js      # Cliente HTTP hacia el backend
│   ├── package.json
│   └── vite.config.js        # Proxy /api → http://localhost:8000
└── README.md
```

---

## Instalación paso a paso

> ⚠️ **Importante:** Los pasos deben realizarse en el orden indicado. Necesitarás **dos terminales abiertas** al mismo tiempo: una para el backend y otra para el frontend.

---

### Paso 1 — Clonar el repositorio

Abre una terminal (CMD, PowerShell o Git Bash) en la carpeta donde quieras guardar el proyecto y ejecuta:

```bash
git clone https://github.com/FestCine-App/FestCine.git
cd FestCine
```

Esto descargará el proyecto completo en una carpeta llamada `FestCine`.

---

### Paso 2 — Crear y cargar la base de datos

#### 2.1 — Crear la base de datos

Abre **pgAdmin** (se instala con PostgreSQL) o una terminal con `psql`:

**Opción A — Desde pgAdmin:**
1. Abre pgAdmin.
2. Clic derecho en "Databases" → "Create" → "Database".
3. En el campo "Database" escribe: `festcine`
4. Clic en "Save".

**Opción B — Desde terminal:**
```bash
psql -U postgres -c "CREATE DATABASE festcine;"
```
Te pedirá la contraseña del usuario `postgres` que configuraste al instalar PostgreSQL.

#### 2.2 — Cargar el script de la base de datos

Este paso crea todas las tablas, datos de prueba, procedimientos almacenados, funciones y triggers.

```bash
psql -U postgres -d festcine -f database/festcinedb.sql
```

> Si ves muchas líneas con `CREATE TABLE`, `INSERT`, `CREATE PROCEDURE`, `CREATE TRIGGER`, etc., el script se ejecutó correctamente.

**Verificar que la carga fue exitosa** — conectarte a la BD y ver las tablas:
```bash
psql -U postgres -d festcine -c "\dt"
```
Debe listar al menos 20 tablas (Peliculas, Asistentes, Proyecciones, Abonos, etc.).

---

### Paso 3 — Configurar el backend

#### 3.1 — Entrar a la carpeta del backend

```bash
cd backend
```

#### 3.2 — Crear el entorno virtual de Python

Un entorno virtual aísla las dependencias del proyecto para no afectar otras instalaciones de Python en tu PC.

```bash
python -m venv venv
```

#### 3.3 — Activar el entorno virtual

**En Windows (CMD o PowerShell):**
```bash
venv\Scripts\activate
```

**En Mac o Linux:**
```bash
source venv/bin/activate
```

> Sabrás que está activo porque el prompt de la terminal cambia a algo como: `(venv) C:\...\FestCine\backend>`

#### 3.4 — Instalar las dependencias de Python

```bash
pip install django==5.2 django-cors-headers pg8000 python-dotenv
```

> Este proceso puede tardar 1-2 minutos dependiendo de tu conexión a internet.

#### 3.5 — Crear el archivo de configuración `.env`

En la carpeta `backend/` crea un archivo llamado **`.env`** (con punto al inicio, sin extensión) con el siguiente contenido:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=festcine
DB_USER=postgres
DB_PASSWORD=aqui_va_tu_contraseña_de_postgres
```

> Reemplaza `aqui_va_tu_contraseña_de_postgres` con la contraseña real que configuraste al instalar PostgreSQL.

**Cómo crear el archivo `.env`:**
- **Windows (Bloc de notas):** Abre el Bloc de notas → pega el contenido → Archivo → Guardar como → navega a la carpeta `backend/` → en "Nombre de archivo" escribe `.env` → en "Tipo" selecciona "Todos los archivos (*.*)" → Guardar.
- **VS Code:** Clic derecho en la carpeta `backend/` en el explorador → "New File" → nombre `.env` → pegar el contenido → guardar.

#### 3.6 — Iniciar el servidor backend

```bash
python manage.py runserver
```

Si todo está correcto, verás algo como:
```
Django version 5.2, using settings 'festcine_backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

> ✅ **Deja esta terminal abierta.** El backend debe permanecer corriendo mientras usas la aplicación.

---

### Paso 4 — Configurar el frontend

> ⚠️ Abre una **segunda terminal** nueva. NO cierres la del backend.

#### 4.1 — Ir a la carpeta del frontend

Desde la raíz del proyecto:
```bash
cd frontend
```

> Si estás en la carpeta `backend/`, primero ejecuta `cd ..` para volver a la raíz, luego `cd frontend`.

#### 4.2 — Instalar las dependencias de Node.js

```bash
npm install
```

> Este proceso descarga las librerías de React y puede tardar 1-3 minutos. Verás una carpeta `node_modules/` crearse automáticamente.

#### 4.3 — Iniciar el servidor del frontend

```bash
npm run dev
```

Verás algo como:
```
  VITE v6.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

> ✅ **Deja esta terminal también abierta.**

---

### Paso 5 — Verificar que todo funciona

Abre tu navegador y entra a:

```
http://localhost:5173
```

Deberías ver la interfaz de FestCine cargada y con datos. Si la pantalla muestra películas, proyecciones y datos del festival, **la instalación fue exitosa**.

> El frontend (puerto 5173) se comunica automáticamente con el backend (puerto 8000) a través del proxy configurado en `vite.config.js`. No necesitas abrir el puerto 8000 manualmente.

---

## Flujos críticos a probar

Una vez que la aplicación esté corriendo, verificar los siguientes flujos antes de la presentación:

### 🎟️ Módulo 1 — Compra de Entrada Individual (P1)

1. Ir a **Taquilla / Comprar Entrada**.
2. Seleccionar una película y una de sus proyecciones disponibles.
3. Seleccionar un asistente y un tipo de tarifa.
4. Hacer clic en "Comprar".
5. ✅ **Resultado esperado (éxito):** mensaje de confirmación con los datos de la entrada.
6. Repetir hasta agotar el aforo de una proyección.
7. ✅ **Resultado esperado (sin cupo):** mensaje amigable "No hay aforo disponible" — sin mostrar código de error SQL.

### 🎫 Módulo T1 — Venta de Abono (Transacción con ROLLBACK)

1. Ir a **Venta de Abonos**.
2. Seleccionar un asistente y un tipo de abono.
3. En "Pasarela de Pago" elegir **"Pago Aprobado"** → hacer clic en "Procesar".
4. ✅ **Resultado esperado:** código de acceso generado y abono registrado.
5. Repetir el proceso pero ahora elegir **"Pago Rechazado (Forzar Fallo y Rollback)"** → hacer clic en "Procesar".
6. ✅ **Resultado esperado:** mensaje de error indicando que el pago falló y no se registró ningún abono (ROLLBACK aplicado).

### 📅 Módulo 2 — Panel de Agenda + Trigger TR1 (Control de Horarios)

1. Ir a **Administración → Programar Proyecciones**.
2. Seleccionar una película, una sala, y una fecha/hora **que NO choque** con ninguna proyección existente.
3. Hacer clic en "Programar Función".
4. ✅ **Resultado esperado:** proyección registrada y aparece en la lista.
5. Intentar programar otra proyección en la **misma sala y un horario que se superponga** (dentro de la duración de la película anterior + 30 minutos de limpieza).
6. ✅ **Resultado esperado:** mensaje de error de cruce de horarios — el Trigger TR1 rechaza la inserción.

### 📊 Reportes

1. Ir a **Reportes → Informe Financiero**.
2. ✅ **Resultado esperado:** tabla con dos tipos de venta diferenciados ("Entrada Individual" y "Abono"), cada uno con sus subcategorías de tarifa, cantidades y subtotales. Total general al pie.
3. Ir a **Reportes → Ranking de Películas**.
4. ✅ **Resultado esperado:** lista de películas con asistentes reales y porcentaje de ocupación de sala.
5. Ir a **Reportes → Acta de Premiación**.
6. ✅ **Resultado esperado:** películas ganadoras por categoría con el promedio de votación del jurado.

---

## Solución de problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `python: command not found` | Python no está en el PATH | Reinstalar Python marcando "Add to PATH", o usar `python3` en lugar de `python` |
| `No module named django` | Entorno virtual no activado | Ejecutar `venv\Scripts\activate` (Windows) antes de `python manage.py runserver` |
| `Error de autenticación en PostgreSQL` | Contraseña incorrecta en `.env` | Verificar que `DB_PASSWORD` en `.env` coincide con la contraseña de PostgreSQL |
| `database "festcine" does not exist` | No se creó la BD en el Paso 2 | Ejecutar `psql -U postgres -c "CREATE DATABASE festcine;"` |
| El script SQL da errores al cargar | Caracteres o encoding | Ejecutar `psql -U postgres -d festcine -f database/festcinedb.sql --set=client_encoding=UTF8` |
| Frontend muestra "servidor no responde" | El backend no está corriendo | Verificar que la terminal del backend muestra "Starting development server at http://127.0.0.1:8000/" |
| `npm: command not found` | Node.js no instalado o no en PATH | Reinstalar Node.js desde https://nodejs.org/ |
| Puerto 8000 o 5173 ya en uso | Otro proceso usa ese puerto | En Windows ejecutar `netstat -ano \| findstr :8000` para ver qué proceso lo usa y cerrarlo |
| `psql: command not found` en Windows | PostgreSQL no está en el PATH | Agregar `C:\Program Files\PostgreSQL\15\bin` al PATH del sistema |
| Trigger TR1 no rechaza el cruce | Datos de prueba sin colisión real | Verificar que la fecha/hora de la nueva proyección esté dentro del rango: hora inicio + duración película + 30 min de la proyección ya existente en esa sala |

---

## Arquitectura del sistema

```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────────────┐
│   FRONTEND (React)  │  HTTP   │  BACKEND (Django API) │  pg8000 │  BASE DE DATOS      │
│   localhost:5173    │────────▶│   localhost:8000      │────────▶│  PostgreSQL          │
│                     │         │                       │         │  festcine            │
│  - Taquilla         │         │  - Rutas REST (/api/) │         │                     │
│  - Venta Abonos     │         │  - Sin lógica SQL     │         │  - Stored Procedures│
│  - Panel Agenda     │         │    en el cliente      │         │    P1, T1           │
│  - Reportes         │         │  - Llama a procs      │         │  - Trigger TR1      │
│                     │         │    almacenados        │         │  - Vistas / DQL     │
└─────────────────────┘         └──────────────────────┘         └─────────────────────┘
```

---

## Integrantes del equipo

> Completar con los nombres del grupo antes de la presentación.

- 
- 
- 
- 

---

*Proyecto Final — Base de Datos — FestCine Sistema de Gestión de Festival de Cine Independiente*
