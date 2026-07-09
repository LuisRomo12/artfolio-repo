# ArtFolio 🌌

**ArtFolio** es un CMS (Content Management System) auto-hospedado y responsivo, diseñado especialmente para artistas visuales independientes. La aplicación permite a los artistas gestionar su inventario de obras y colecciones de manera privada, mientras ofrece una galería pública interactiva e inmersiva con una propuesta estética única de temática dual: **Y2K / Retro Windows 95** y **Gótico / Cybersigilismo**.

---

## 🚀 Características Principales

*   **Temática Dual:** Alterna entre una interfaz nostálgica de escritorio interactivo Y2K (con ventanas arrastrables, MS Paint funcional, reloj en tiempo real y smiley interactivo) y un diseño gótico/cybersigil minimalista y elegante.
*   **Gestión de Inventario (CMS):** Panel de administración privado para crear, leer, actualizar y eliminar (CRUD) obras y colecciones.
*   **Subida a la Nube:** Integración directa con el SDK de Cloudinary para almacenar y servir imágenes optimizadas mediante CDN.
*   **Seguridad:** Autenticación de administrador protegida con JSON Web Tokens (JWT) firmados digitalmente, hashing de contraseñas con `bcrypt`, sanitización estricta de entradas contra inyección de código (XSS) y políticas CORS restrictivas por entorno.
*   **API REST Autodocumentada:** Backend construido con FastAPI, que expone automáticamente documentación interactiva en `/docs` y `/redoc`.

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

*   [Python 3.10+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/)
*   [PostgreSQL 14+](https://www.postgresql.org/download/)
*   [Git](https://git-scm.com/)

---

## ⚙️ Instalación y Configuración

El proyecto está estructurado de manera cliente-servidor en dos carpetas principales: `backend` y `frontend`.

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd "y2k edicion"
```

### 2. Configurar el Backend

1. Entra al directorio del backend:
   ```bash
   cd backend
   ```
2. Crea e inicia un entorno virtual de Python:
   *   **En Windows (PowerShell):**
       ```powershell
       python -m venv venv
       .\venv\Scripts\Activate.ps1
       ```
   *   **En macOS/Linux:**
       ```bash
       python3 -m venv venv
       source venv/bin/activate
       ```
3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura tus variables de entorno:
   *   Duplica el archivo de ejemplo `.env.example` y renómbralo a `.env`:
       ```bash
       cp .env.example .env
       ```
   *   Abre el archivo `.env` y edita las siguientes variables con tus credenciales de PostgreSQL, claves JWT, llaves de Cloudinary y dominios autorizados de CORS:
       ```env
       DATABASE_URL=postgresql://<usuario>:<password>@localhost:5432/<nombre_db>
       JWT_SECRET_KEY=tu_clave_secreta_para_firmar_tokens
       CLOUDINARY_CLOUD_NAME=tu_cloud_name
       CLOUDINARY_API_KEY=tu_api_key
       CLOUDINARY_API_SECRET=tu_api_secret
       ALLOWED_ORIGINS=http://localhost:5173
       ```

### 3. Configurar el Frontend

1. Desde la raíz del proyecto, ingresa a la carpeta del frontend:
   ```bash
   cd ../frontend
   ```
2. Instala los paquetes y dependencias de Node:
   ```bash
   npm install
   ```

---

## 🗄️ Inicialización de la Base de Datos

Una vez configurado tu archivo `.env` en el backend, es obligatorio inicializar y poblar tu base de datos local en PostgreSQL. Corre los siguientes comandos **desde la carpeta `backend`** en tu terminal activa (con el entorno virtual encendido):

1. **Crear las tablas de la base de datos (Migración):**
   ```bash
   python scripts/db_migrate.py
   ```
2. **Cargar los datos iniciales de prueba (Seed):**
   ```bash
   python scripts/seed_data.py
   ```
   *Esto creará un usuario administrador inicial con el correo `artista@artfolio.com` y contraseña `artista123`, además de colecciones y obras de demostración.*

---

## 🏃 Ejecución del Proyecto

Para levantar la aplicación por completo, debes iniciar ambos servidores simultáneamente en terminales separadas:

### Iniciar Backend (FastAPI)
Desde la carpeta `backend` con el entorno virtual activo:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
*   **API local:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
*   **Documentación Interactiva (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Iniciar Frontend (Vue 3 + Vite)
Desde la carpeta `frontend`:
```bash
npm run dev
```
*   **Aplicación web local:** [http://localhost:5173](http://localhost:5173)

---

## 🧪 Pruebas Unitarias

### Backend (Pytest)
Las pruebas unitarias del backend se ejecutan con `pytest`. Para ver la guía detallada de ejecución y los 24 casos de prueba cubiertos, consulta el archivo [README-tests.md](file:///c:/uta/9-c/desarrollo%20web%20integral/y2k%20edicion/backend/README-tests.md) en el directorio `backend`.

Para ejecutar las pruebas directamente, desde la carpeta `backend`:
```bash
python -m pytest
```

### Frontend (Vitest)
Desde la carpeta `frontend`:
```bash
npm run test
```
