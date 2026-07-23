# Diapositivas para la Presentación del Avance (75%)
## Proyecto: ArtFolio

Este documento contiene la estructura y textos listos para usar en tus diapositivas o mostrar en pantalla durante la grabación del video.

---

## 🗂️ Diapositiva 1: Metodología Ágil y Backlog de Producto

### **Historia de Usuario 1: Selector de Tema Dual (UI/UX)**
*   **Como** visitante de la galería pública,
*   **quiero** alternar entre la interfaz Y2K (Windows 95) y la interfaz Gótica (Cybersigilism),
*   **para** experimentar las dos propuestas estéticas del portafolio.
*   **Criterios de Aceptación:**
    1.  El usuario puede cambiar el tema mediante un botón persistiendo su elección en `localStorage`.
    2.  Las ventanas arrastrables, MS Paint interactivo y el smiley animado son exclusivos del tema Y2K.
    3.  El tema Gótico carga una interfaz minimalista, oscura y elegante.

### **Historia de Usuario 2: Carga de Obras en la Nube (Cloudinary)**
*   **Como** artista visual autenticado,
*   **quiero** subir archivos de imagen a la nube al crear o editar una obra,
*   **para** que los assets de mi portafolio se carguen rápido y se sirvan mediante una CDN.
*   **Criterios de Aceptación:**
    1.  El sistema valida y restringe formatos de imagen permitidos (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`).
    2.  Los archivos se guardan automáticamente en la carpeta `"artfolio"` de Cloudinary.
    3.  La base de datos almacena el string de la URL segura (`secure_url`) devuelto por la API.

### **Historia de Usuario 3: Seguridad de Sesión Administrativa (JWT)**
*   **Como** administrador del sitio,
*   **quiero** que todas las rutas del panel privado estén restringidas por tokens JWT,
*   **para** evitar que usuarios no autorizados alteren el inventario de obras y colecciones.
*   **Criterios de Aceptación:**
    1.  La navegación directa a `/dashboard` sin un token activo redirige al usuario a `/login`.
    2.  El backend valida la firma digital y expiración de los tokens en cada endpoint sensible usando inyección de dependencias de FastAPI.
    3.  Las contraseñas de los usuarios se almacenan en PostgreSQL cifradas bajo el algoritmo seguro `bcrypt`.

---

## 💻 Diapositiva 2: Solución al Reto de Codificación en Windows

### **El Problema:**
Durante las pruebas de integración local en sistemas Windows, la conexión por defecto de PostgreSQL utilizaba una codificación regional (ej. WIN1252), lo que corrompía caracteres con acentos o caracteres especiales (ej. `"En exhibición"`, `"Óleo sobre lienzo"`) y provocaba fallos de escritura en las tablas de la base de datos.

### **La Solución:**
Forzar explícitamente el parámetro `client_encoding` a `"UTF8"` durante el parseo de la cadena de conexión de la base de datos en la inicialización del Pool de Conexiones de psycopg2.

### **Código Implementado (`backend/app/database.py`):**

```python
from urllib.parse import urlparse

def _parse_db_url(url: str) -> dict:
    """
    Parsea DATABASE_URL en argumentos clave de psycopg2.
    Agrega client_encoding='UTF8' para corregir la escritura de acentos en Windows.
    """
    p = urlparse(url)
    return {
        "host": p.hostname,
        "port": p.port or 5432,
        "user": p.username,
        "password": p.password,
        "dbname": p.path.lstrip("/"),
        
        # SOLUCIÓN DE CODIFICACIÓN PARA WINDOWS Y CARACTERES ESPECIALES:
        "client_encoding": "UTF8", 
    }
```

---

## 🚀 Diapositiva 3: Mapa de Ruta (Roadmap) - 25% Restante

### **1. Despliegue en la Nube (Cloud Deployment)**
*   **Servidor Backend (FastAPI):** Alojado en **Render** mediante plantillas blueprint automatizadas (`render.yaml`).
*   **Cliente Frontend (Vue 3 + Vite):** Publicado en **Vercel** configurando el router SPA en `vercel.json`.
*   **Persistencia:** Configuración del servidor gestionado de PostgreSQL en producción con variables de entorno protegidas.

### **2. Pruebas Finales End-to-End (E2E)**
*   Ejecución de baterías de pruebas de integración de endpoints en el entorno de producción (Staging).
*   Pruebas de visualización y responsividad cross-browser (Chrome, Firefox, Safari).
*   Auditorías de seguridad (verificación de HTTPS y expiración correcta de las sesiones JWT).

### **3. Entrega al Cliente**
*   Traspaso del reporte técnico de arquitectura (`REPORTE_TECNICO.md`).
*   Entrega del manual de usuario para el artista independiente (`MANUAL_USUARIO.md`).
*   Configuración final de credenciales administrativas y entrega de accesos privados.
