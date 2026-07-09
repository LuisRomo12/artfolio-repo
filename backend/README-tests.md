# Pruebas Unitarias del Backend (FastAPI)

Este directorio contiene la suite de pruebas unitarias automatizadas para la API de ArtFolio. Las pruebas están diseñadas para ejecutarse de forma completamente aislada utilizando mocks para simular las llamadas a la base de datos PostgreSQL (`psycopg2`) y al SDK de almacenamiento de imágenes de Cloudinary, evitando depender de servicios externos o alterar la base de datos de desarrollo real.

---

## 🛠️ Requisitos de Ejecución

Asegúrate de tener instaladas las dependencias del backend especificadas en el archivo `requirements.txt`, incluyendo `pytest`:

```bash
cd backend
pip install -r requirements.txt
```

---

## 🚀 Cómo Correr las Pruebas

Para ejecutar toda la suite de pruebas unitarias, ejecuta el siguiente comando desde la carpeta `/backend/`:

```bash
python -m pytest
```

Para ver una salida más detallada con el nombre de cada prueba ejecutada individualmente:

```bash
python -m pytest -v
```

---

## 📋 Detalle de Casos de Prueba Evaluados

A continuación se presenta la tabla resumen de los 24 casos de prueba cubiertos, organizados por módulo y endpoint:

| Módulo / Endpoint | Caso de Prueba / Descripción | Resultado |
| :--- | :--- | :---: |
| **Inicio & Estado** | | |
| `GET /` | Retorna el mensaje de bienvenida del servidor API. | **PASÓ** |
| `GET /health` | Retorna el estado saludable de la API (`"status": "healthy"`). | **PASÓ** |
| **Autenticación (`/auth`)** | | |
| `POST /auth/register` | Registro exitoso de un nuevo perfil de artista. | **PASÓ** |
| `POST /auth/register` | Intento de registro con contraseña menor a 6 caracteres (falla 422). | **PASÓ** |
| `POST /auth/register` | Intento de registro con correo duplicado / ya existente (falla 400). | **PASÓ** |
| `POST /auth/login` | Inicio de sesión exitoso con credenciales correctas (retorna JWT). | **PASÓ** |
| `POST /auth/login` | Intento de login con credenciales incorrectas o inexistentes (falla 401). | **PASÓ** |
| **Colecciones (`/collections`)** | | |
| `GET /collections/` | Obtención de lista pública de colecciones de arte. | **PASÓ** |
| `GET /collections/{id}` | Recuperación exitosa de detalles de una colección existente. | **PASÓ** |
| `GET /collections/{id}` | Búsqueda de colección inexistente retorna error 404. | **PASÓ** |
| `POST /collections/` | Intento de creación de colección sin cabecera de autenticación (falla 401). | **PASÓ** |
| `POST /collections/` | Creación exitosa de colección con token JWT válido. | **PASÓ** |
| `PUT /collections/{id}` | Actualización de los datos de una colección existente con token válido. | **PASÓ** |
| `DELETE /collections/{id}` | Eliminación exitosa de una colección vacía con token válido. | **PASÓ** |
| **Obras de Arte (`/artworks`)** | | |
| `GET /artworks/` | Obtención de la galería pública completa de obras de arte. | **PASÓ** |
| `GET /artworks/` | Filtrado correcto de obras asociadas a un `coleccion_id` específico. | **PASÓ** |
| `GET /artworks/{id}` | Recuperación exitosa de los detalles de una obra existente. | **PASÓ** |
| `GET /artworks/{id}` | Búsqueda de obra inexistente retorna error 404. | **PASÓ** |
| `POST /artworks/upload` | Subida exitosa de archivo de imagen (simula SDK de Cloudinary) con token. | **PASÓ** |
| `POST /artworks/upload` | Intento de subir tipo de archivo no permitido (ej. PDF) (falla 400). | **PASÓ** |
| `POST /artworks/` | Creación de obra sin token de autorización (falla 401). | **PASÓ** |
| `POST /artworks/` | Creación de obra exitosa con parámetros válidos y token. | **PASÓ** |
| `POST /artworks/` | Intento de crear obra con estado inválido fuera de CHECK (`Disponible`, `Vendida`, `En exhibición`) (falla 422). | **PASÓ** |
| `PUT /artworks/{id}` | Edición exitosa de los datos de una obra con token. | **PASÓ** |
| `DELETE /artworks/{id}` | Eliminación exitosa de una obra de arte con token. | **PASÓ** |
