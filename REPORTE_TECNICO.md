# Reporte Técnico de ArtFolio

Este documento recopila la información técnica estructurada, código fuente clave y configuraciones del repositorio ArtFolio.

---

## 1. ARQUITECTURA Y PATRONES

### Estructura de Directorios (3 niveles)

#### Backend (`/backend`)
```text
backend
├── .env
├── .env.example
├── pytest.ini
├── requirements.txt
├── app
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── __init__.py
│   ├── routes
│   │   ├── artworks.py
│   │   ├── auth.py
│   │   ├── collections.py
│   │   └── __init__.py
│   └── utils
│       ├── security.py
│       └── __init__.py
├── scripts
│   ├── db_migrate.py
│   └── seed_data.py
├── static
│   └── uploads
└── tests
    ├── __init__.py
    ├── test_artworks.py
    ├── test_auth.py
    ├── test_collections.py
    └── test_main.py
```

#### Frontend (`/frontend`)
```text
frontend
├── index.html
├── package.json
├── vite.config.js
├── public
│   ├── favicon.svg
│   └── icons.svg
├── src
│   ├── App.vue
│   ├── main.js
│   ├── style.css
│   ├── assets
│   │   ├── hero.png
│   │   ├── vite.svg
│   │   └── vue.svg
│   ├── components
│   │   └── HelloWorld.vue
│   ├── router
│   │   └── index.js
│   └── views
│       ├── AdminDashboard.vue
│       ├── LoginView.vue
│       └── PublicGallery.vue
└── tests
    ├── LoginView.spec.js
    └── router.spec.js
```

---

### Patrones de Diseño Identificados

#### 1. Pool de Conexiones Singleton y Manejo por Context Manager
*   **Nombre del Patrón:** Singleton (Pool de Conexiones) / Context Manager
*   **Archivos:** `backend/app/database.py`
*   **Fragmento de código:**
```python
db_pool = None

def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            conn_kwargs = _parse_db_url(settings.DATABASE_URL)
            db_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1, maxconn=20, **conn_kwargs
            )
...
@contextmanager
def get_db_connection():
    global db_pool
    if db_pool is None:
        init_db_pool()
    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        db_pool.putconn(conn)
```

#### 2. DTO (Data Transfer Object) y Esquemas de Validación
*   **Nombre del Patrón:** Data Transfer Object (DTO) implementado mediante esquemas Pydantic para separar el payload de entrada de la respuesta JSON final.
*   **Archivos:** `backend/app/models.py`
*   **Fragmento de código:**
```python
class ArtworkBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    tecnica: str = Field(..., max_length=255)
    dimensiones: str = Field(..., max_length=100)
    ano: int = Field(..., description="Year of creation")
    precio: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    imagen_url: str = Field(..., description="URL or relative path to the uploaded artwork image")
    estado: str = Field(..., pattern="^(Disponible|Vendida|En exhibición)$")
    coleccion_id: Optional[int] = None

class ArtworkCreate(ArtworkBase):
    pass

class ArtworkResponse(ArtworkBase):
    id: int
    created_at: datetime
```

#### 3. Inyección de Dependencias
*   **Nombre del Patrón:** Dependency Injection (FastAPI Depends) para validación de tokens y recuperación de usuarios autenticados.
*   **Archivos:** `backend/app/routes/auth.py` (definición), `backend/app/routes/artworks.py` y `backend/app/routes/collections.py` (uso)
*   **Fragmento de código:**
```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # (Descifrado y validación del JWT...)
    with get_db_cursor() as cur:
        cur.execute("SELECT id, email, created_at FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        if user is None:
            raise credentials_exception
    return {"id": user[0], "email": user[1], "created_at": user[2]}

# Uso en endpoints
@router.post("/", response_model=ArtworkResponse, status_code=status.HTTP_201_CREATED)
async def create_artwork(
    artwork: ArtworkCreate,
    current_user: dict = Depends(get_current_user)
):
...
```

---

### Comunicación Frontend y Backend
*   **Protocolo:** HTTP/1.1 de forma síncrona / HTTPS (en producción).
*   **Formato de datos:** JSON para el payload de petición y respuesta (`application/json`), excepto el endpoint de subida de imágenes (`/artworks/upload`) que recibe `multipart/form-data`.
*   **Manejo de errores:** El backend levanta excepciones `HTTPException` con códigos de estado estándar de FastAPI (400, 401, 404, 409, 500, 502). El frontend captura estos errores mediante bloques `try/catch` de JavaScript en las llamadas `fetch` y lee el JSON `{ "detail": "Mensaje de error" }` para mostrárselo al usuario de manera controlada.

---

## 2. BASE DE DATOS

### Script de Migración Completo (`db_migrate.py`)
```python
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Resolve paths to locate environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
root_dir = os.path.dirname(backend_dir)

# Load variables from potential .env locations
load_dotenv(os.path.join(backend_dir, ".env"))
load_dotenv(os.path.join(root_dir, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not defined.")
    print("Please configure it in a '.env' file inside the backend folder or system environment.")
    sys.exit(1)

SQL_STATEMENTS = [
    # 1. Create usuarios Table
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # 2. Create colecciones Table
    """
    CREATE TABLE IF NOT EXISTS colecciones (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE NOT NULL,
        descripcion TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # 3. Create obras Table
    """
    CREATE TABLE IF NOT EXISTS obras (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(255) NOT NULL,
        tecnica VARCHAR(255) NOT NULL,
        dimensiones VARCHAR(100) NOT NULL,
        ano INTEGER NOT NULL,
        precio NUMERIC(10, 2) DEFAULT NULL,
        imagen_url TEXT NOT NULL,
        estado VARCHAR(50) NOT NULL CHECK (estado IN ('Disponible', 'Vendida', 'En exhibición')),
        coleccion_id INTEGER REFERENCES colecciones(id) ON DELETE SET NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # 4. Create Indexes for optimization
    "CREATE INDEX IF NOT EXISTS idx_obras_coleccion_id ON obras(coleccion_id);",
    "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);"
]

def run_migrations():
    print(f"Connecting to database specified in DATABASE_URL...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        
        with conn.cursor() as cur:
            for i, stmt in enumerate(SQL_STATEMENTS, 1):
                clean_stmt = stmt.strip()
                first_line = clean_stmt.splitlines()[0] if clean_stmt else ""
                print(f"[{i}/{len(SQL_STATEMENTS)}] Executing: {first_line}...")
                cur.execute(stmt)
        
        conn.commit()
        print("Database migrations applied successfully!")
        conn.close()
    except Exception as e:
        print(f"Migration failed and rolled back due to error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
```

---

### Tablas y Esquema

#### 1. Tabla `usuarios`
| Nombre Columna | Tipo de Dato | Restricciones |
| :--- | :--- | :--- |
| `id` | `SERIAL` (INTEGER) | `PRIMARY KEY` |
| `email` | `VARCHAR(255)` | `UNIQUE`, `NOT NULL` |
| `password_hash`| `VARCHAR(255)` | `NOT NULL` |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `DEFAULT CURRENT_TIMESTAMP` |

#### 2. Tabla `colecciones`
| Nombre Columna | Tipo de Dato | Restricciones |
| :--- | :--- | :--- |
| `id` | `SERIAL` (INTEGER) | `PRIMARY KEY` |
| `nombre` | `VARCHAR(255)` | `UNIQUE`, `NOT NULL` |
| `descripcion` | `TEXT` | Ninguna |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `DEFAULT CURRENT_TIMESTAMP` |

#### 3. Tabla `obras`
| Nombre Columna | Tipo de Dato | Restricciones |
| :--- | :--- | :--- |
| `id` | `SERIAL` (INTEGER) | `PRIMARY KEY` |
| `titulo` | `VARCHAR(255)` | `NOT NULL` |
| `tecnica` | `VARCHAR(255)` | `NOT NULL` |
| `dimensiones` | `VARCHAR(100)` | `NOT NULL` |
| `ano` | `INTEGER` | `NOT NULL` |
| `precio` | `NUMERIC(10, 2)` | `DEFAULT NULL` |
| `imagen_url` | `TEXT` | `NOT NULL` |
| `estado` | `VARCHAR(50)` | `NOT NULL`, `CHECK (estado IN ('Disponible', 'Vendida', 'En exhibición'))` |
| `coleccion_id` | `INTEGER` | `FOREIGN KEY REFERENCES colecciones(id) ON DELETE SET NULL` |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `DEFAULT CURRENT_TIMESTAMP` |

---

### Relaciones entre Tablas
*   **`colecciones` a `obras`:** Una relación **Uno a Muchos** (Una colección puede contener múltiples obras; una obra puede opcionalmente pertenecer a una sola colección). Está regulado por `coleccion_id` en la tabla `obras` con restricción de eliminación en cascada anulada (`ON DELETE SET NULL`).

---

## 3. API PROPIA (endpoints backend)

### 1. `GET /` (Welcome root)
*   **Autenticación:** No
*   **Parámetros:** Ninguno
*   **Respuesta exitosa (JSON):**
    ```json
    { "message": "Welcome to ArtFolio API" }
    ```
*   **Códigos de error:** Ninguno
*   **Código de la función:**
    ```python
    @app.get("/")
    async def root():
        return {"message": "Welcome to ArtFolio API"}
    ```

### 2. `GET /health` (Health Check)
*   **Autenticación:** No
*   **Parámetros:** Ninguno
*   **Respuesta exitosa (JSON):**
    ```json
    { "status": "healthy" }
    ```
*   **Códigos de error:** Ninguno
*   **Código de la función:**
    ```python
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    ```

### 3. `POST /auth/register` (Register User)
*   **Autenticación:** No
*   **Parámetros (Body - JSON):**
    *   `email`: string (EmailStr, requerido)
    *   `password`: string (min_length=8, requerido)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "id": 1,
      "email": "artista@artfolio.com",
      "created_at": "2026-07-09T08:00:00Z"
    }
    ```
*   **Códigos de error:**
    *   `400 Bad Request`: "El correo electrónico ya está registrado"
    *   `422 Unprocessable Entity`: Formato de email inválido o contraseña inferior a 8 caracteres.
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    async def register(user: UserCreate):
        hashed_pwd = get_password_hash(user.password)
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM usuarios WHERE email = %s", (user.email,))
                if cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El correo electrónico ya está registrado"
                    )
                cur.execute(
                    "INSERT INTO usuarios (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at",
                    (user.email, hashed_pwd)
                )
                new_user = cur.fetchone()
            return {
                "id": new_user[0],
                "email": new_user[1],
                "created_at": new_user[2]
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar usuario: {str(e)}"
            )
    ```

### 4. `POST /auth/login` (Login User)
*   **Autenticación:** No
*   **Parámetros (Body - JSON):**
    *   `email`: string (EmailStr, requerido)
    *   `password`: string (requerido)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1Ni...",
      "token_type": "bearer"
    }
    ```
*   **Códigos de error:**
    *   `401 Unauthorized`: "Correo o contraseña incorrectos"
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.post("/login", response_model=Token)
    async def login(credentials: UserCreate):
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id, email, password_hash FROM usuarios WHERE email = %s", (credentials.email,))
                user = cur.fetchone()
            if not user or not verify_password(credentials.password, user[2]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Correo o contraseña incorrectos",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user[1]}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en el servidor durante el login: {str(e)}"
            )
    ```

### 5. `GET /collections/` (List Collections)
*   **Autenticación:** No
*   **Parámetros:** Ninguno
*   **Respuesta exitosa (JSON):**
    ```json
    [
      {
        "id": 1,
        "nombre": "Mitologías Perdidas",
        "descripcion": "Descripción conceptual...",
        "created_at": "2026-07-09T08:00:00Z"
      }
    ]
    ```
*   **Códigos de error:** `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.get("/", response_model=List[CollectionResponse])
    async def get_collections():
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id, nombre, descripcion, created_at FROM colecciones ORDER BY nombre ASC")
                rows = cur.fetchall()
            collections = []
            for row in rows:
                collections.append({
                    "id": row[0],
                    "nombre": row[1],
                    "descripcion": row[2],
                    "created_at": row[3]
                })
            return collections
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener colecciones: {str(e)}"
            )
    ```

### 6. `GET /collections/{collection_id}` (Retrieve Collection)
*   **Autenticación:** No
*   **Parámetros (Path):**
    *   `collection_id`: integer (requerido)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "id": 1,
      "nombre": "Mitologías Perdidas",
      "descripcion": "Descripción de la colección",
      "created_at": "2026-07-09T08:00:00Z"
    }
    ```
*   **Códigos de error:**
    *   `404 Not Found`: "Colección no encontrada"
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.get("/{collection_id}", response_model=CollectionResponse)
    async def get_collection(collection_id: int):
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id, nombre, descripcion, created_at FROM colecciones WHERE id = %s", (collection_id,))
                row = cur.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Colección no encontrada"
                )
            return {
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2],
                "created_at": row[3]
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener la colección: {str(e)}"
            )
    ```

### 7. `POST /collections/` (Create Collection)
*   **Autenticación:** Sí (HTTP Bearer token)
*   **Parámetros (Body - JSON):**
    *   `nombre`: string (máx 255 letras, XSS Sanitized, requerido)
    *   `descripcion`: string (opcional, XSS Sanitized)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "id": 2,
      "nombre": "Anatomía de la Melancolía",
      "descripcion": "Estudios de claroscuro...",
      "created_at": "2026-07-09T08:05:00Z"
    }
    ```
*   **Códigos de error:**
    *   `400 Bad Request`: "Ya existe una colección con este nombre"
    *   `401 Unauthorized`: Token expirado, inválido o ausente
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
    async def create_collection(
        collection: CollectionCreate,
        current_user: dict = Depends(get_current_user)
    ):
        try:
            with get_db_cursor() as cur:
                cur.execute(
                    "INSERT INTO colecciones (nombre, descripcion) VALUES (%s, %s) RETURNING id, nombre, descripcion, created_at",
                    (collection.nombre, collection.descripcion)
                )
                row = cur.fetchone()
            return {
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2],
                "created_at": row[3]
            }
        except UniqueViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una colección con este nombre"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear colección: {str(e)}"
            )
    ```

### 8. `PUT /collections/{collection_id}` (Update Collection)
*   **Autenticación:** Sí (HTTP Bearer token)
*   **Parámetros (Path + Body - JSON):**
    *   `collection_id`: integer (path, requerido)
    *   `nombre`: string (body, max_length=255, XSS Sanitized, requerido)
    *   `descripcion`: string (body, opcional, XSS Sanitized)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "id": 2,
      "nombre": "Anatomía Editada",
      "descripcion": "Nueva descripción...",
      "created_at": "2026-07-09T08:05:00Z"
    }
    ```
*   **Códigos de error:**
    *   `400 Bad Request`: "Ya existe otra colección con este nombre"
    *   `401 Unauthorized`: Token inválido o expirado
    *   `404 Not Found`: "Colección no encontrada"
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.put("/{collection_id}", response_model=CollectionResponse)
    async def update_collection(
        collection_id: int,
        collection: CollectionCreate,
        current_user: dict = Depends(get_current_user)
    ):
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM colecciones WHERE id = %s", (collection_id,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Colección no encontrada"
                    )
                cur.execute(
                    "UPDATE colecciones SET nombre = %s, descripcion = %s WHERE id = %s RETURNING id, nombre, descripcion, created_at",
                    (collection.nombre, collection.descripcion, collection_id)
                )
                row = cur.fetchone()
            return {
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2],
                "created_at": row[3]
            }
        except UniqueViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otra colección con este nombre"
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar la colección: {str(e)}"
            )
    ```

### 9. `DELETE /collections/{collection_id}` (Delete Collection)
*   **Autenticación:** Sí (HTTP Bearer token)
*   **Parámetros (Path):**
    *   `collection_id`: integer (requerido)
*   **Respuesta exitosa (JSON):**
    ```json
    { "message": "Colección eliminada exitosamente" }
    ```
*   **Códigos de error:**
    *   `401 Unauthorized`
    *   `404 Not Found`: "Colección no encontrada"
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.delete("/{collection_id}", status_code=status.HTTP_200_OK)
    async def delete_collection(
        collection_id: int,
        current_user: dict = Depends(get_current_user)
    ):
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM colecciones WHERE id = %s", (collection_id,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Colección no encontrada"
                    )
                cur.execute("DELETE FROM colecciones WHERE id = %s", (collection_id,))
            return {"message": "Colección eliminada exitosamente"}
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar la colección: {str(e)}"
            )
    ```

### 10. `GET /artworks/` (List Artworks)
*   **Autenticación:** No
*   **Parámetros (Query - Opcional):**
    *   `coleccion_id`: integer (filtra las obras pertenecientes a esa colección)
*   **Respuesta exitosa (JSON):**
    ```json
    [
      {
        "id": 5,
        "titulo": "El Lamento de Ícaro",
        "tecnica": "Óleo sobre lienzo",
        "dimensiones": "120 x 90 cm",
        "ano": 2024,
        "precio": 1200.00,
        "imagen_url": "https://images.unsplash.com/...",
        "estado": "Disponible",
        "coleccion_id": 1,
        "created_at": "2026-07-09T08:00:00Z"
      }
    ]
    ```
*   **Códigos de error:** `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.get("/", response_model=List[ArtworkResponse])
    async def get_artworks(
        coleccion_id: Optional[int] = Query(None, description="Filtrar obras por ID de colección")
    ):
        try:
            with get_db_cursor() as cur:
                if coleccion_id is not None:
                    cur.execute(
                        "SELECT id, titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id, created_at "
                        "FROM obras WHERE coleccion_id = %s ORDER BY created_at DESC",
                        (coleccion_id,)
                    )
                else:
                    cur.execute(
                        "SELECT id, titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id, created_at "
                        "FROM obras ORDER BY created_at DESC"
                    )
                rows = cur.fetchall()
            artworks = []
            for row in rows:
                artworks.append({
                    "id": row[0],
                    "titulo": row[1],
                    "tecnica": row[2],
                    "dimensiones": row[3],
                    "ano": row[4],
                    "precio": row[5],
                    "imagen_url": row[6],
                    "estado": row[7],
                    "coleccion_id": row[8],
                    "created_at": row[9]
                })
            return artworks
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener obras: {str(e)}"
            )
    ```

### 11. `GET /artworks/{artwork_id}` (Retrieve Artwork)
*   **Autenticación:** No
*   **Parámetros (Path):**
    *   `artwork_id`: integer (requerido)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "id": 5,
      "titulo": "El Lamento de Ícaro",
      "tecnica": "Óleo sobre lienzo",
      "dimensiones": "120 x 90 cm",
      "ano": 2024,
      "precio": 1200.00,
      "imagen_url": "https://images.unsplash.com/...",
      "estado": "Disponible",
      "coleccion_id": 1,
      "created_at": "2026-07-09T08:00:00Z"
    }
    ```
*   **Códigos de error:**
    *   `404 Not Found`: "Obra no encontrada"
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.get("/{artwork_id}", response_model=ArtworkResponse)
    async def get_artwork(artwork_id: int):
        try:
            with get_db_cursor() as cur:
                cur.execute(
                    "SELECT id, titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id, created_at "
                    "FROM obras WHERE id = %s",
                    (artwork_id,)
                )
                row = cur.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Obra no encontrada"
                )
            return {
                "id": row[0],
                "titulo": row[1],
                "tecnica": row[2],
                "dimensiones": row[3],
                "ano": row[4],
                "precio": row[5],
                "imagen_url": row[6],
                "estado": row[7],
                "coleccion_id": row[8],
                "created_at": row[9]
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener la obra: {str(e)}"
            )
    ```

### 12. `POST /artworks/` (Create Artwork)
*   **Autenticación:** Sí (HTTP Bearer token)
*   **Parámetros (Body - JSON):**
    *   `titulo`: string (max_length=255, XSS Sanitized, requerido)
    *   `tecnica`: string (max_length=255, XSS Sanitized, requerido)
    *   `dimensiones`: string (max_length=100, XSS Sanitized, requerido)
    *   `ano`: integer (requerido)
    *   `precio`: decimal/null (max_digits=10, decimal_places=2, opcional)
    *   `imagen_url`: string (requerido)
    *   `estado`: string (valores válidos: "Disponible", "Vendida", "En exhibición", requerido)
    *   `coleccion_id`: integer/null (opcional)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "id": 6,
      "titulo": "Memento Mori II",
      "tecnica": "Óleo y pan de oro",
      "dimensiones": "80 x 80 cm",
      "ano": 2025,
      "precio": 950.00,
      "imagen_url": "https://res.cloudinary.com/...",
      "estado": "Disponible",
      "coleccion_id": 1,
      "created_at": "2026-07-09T08:10:00Z"
    }
    ```
*   **Códigos de error:**
    *   `400 Bad Request`: "Estado inválido. Debe ser uno de: ..." o "La colección especificada no existe" o error de violación de clave foránea.
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.post("/", response_model=ArtworkResponse, status_code=status.HTTP_201_CREATED)
    async def create_artwork(
        artwork: ArtworkCreate,
        current_user: dict = Depends(get_current_user)
    ):
        valid_states = {"Disponible", "Vendida", "En exhibición"}
        if artwork.estado not in valid_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}"
            )
        try:
            with get_db_cursor() as cur:
                if artwork.coleccion_id is not None:
                    cur.execute("SELECT id FROM colecciones WHERE id = %s", (artwork.coleccion_id,))
                    if not cur.fetchone():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La colección especificada no existe"
                        )
                cur.execute(
                    "INSERT INTO obras (titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id, titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id, created_at",
                    (
                        artwork.titulo, artwork.tecnica, artwork.dimensiones, artwork.ano,
                        artwork.precio, artwork.imagen_url, artwork.estado, artwork.coleccion_id
                    )
                )
                row = cur.fetchone()
            return {
                "id": row[0], "titulo": row[1], "tecnica": row[2], "dimensiones": row[3],
                "ano": row[4], "precio": row[5], "imagen_url": row[6], "estado": row[7],
                "coleccion_id": row[8], "created_at": row[9]
            }
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad: la colección referenciada no existe"
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear obra: {str(e)}"
            )
    ```

### 13. `PUT /artworks/{artwork_id}` (Update Artwork)
*   **Autenticación:** Sí (HTTP Bearer token)
*   **Parámetros (Path + Body - JSON):**
    *   `artwork_id`: integer (path, requerido)
    *   `titulo`, `tecnica`, `dimensiones`, `ano`, `precio`, `imagen_url`, `estado`, `coleccion_id` (body, igual al POST)
*   **Respuesta exitosa (JSON):**
    ```json
    {
      "id": 6,
      "titulo": "Memento Mori II (Editada)",
      "tecnica": "Óleo y pan de oro",
      "dimensiones": "80 x 80 cm",
      "ano": 2025,
      "precio": 1000.00,
      "imagen_url": "https://res.cloudinary.com/...",
      "estado": "Vendida",
      "coleccion_id": 1,
      "created_at": "2026-07-09T08:10:00Z"
    }
    ```
*   **Códigos de error:**
    *   `400 Bad Request`: Errores de validación de campos, estados o IDs de colección
    *   `401 Unauthorized`
    *   `404 Not Found`: "Obra no encontrada"
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.put("/{artwork_id}", response_model=ArtworkResponse)
    async def update_artwork(
        artwork_id: int,
        artwork: ArtworkCreate,
        current_user: dict = Depends(get_current_user)
    ):
        valid_states = {"Disponible", "Vendida", "En exhibición"}
        if artwork.estado not in valid_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}"
            )
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM obras WHERE id = %s", (artwork_id,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Obra no encontrada"
                    )
                if artwork.coleccion_id is not None:
                    cur.execute("SELECT id FROM colecciones WHERE id = %s", (artwork.coleccion_id,))
                    if not cur.fetchone():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La colección especificada no existe"
                        )
                cur.execute(
                    "UPDATE obras SET titulo = %s, tecnica = %s, dimensiones = %s, ano = %s, precio = %s, "
                    "imagen_url = %s, estado = %s, coleccion_id = %s WHERE id = %s "
                    "RETURNING id, titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id, created_at",
                    (
                        artwork.titulo, artwork.tecnica, artwork.dimensiones, artwork.ano, artwork.precio,
                        artwork.imagen_url, artwork.estado, artwork.coleccion_id, artwork_id
                    )
                )
                row = cur.fetchone()
            return {
                "id": row[0], "titulo": row[1], "tecnica": row[2], "dimensiones": row[3],
                "ano": row[4], "precio": row[5], "imagen_url": row[6], "estado": row[7],
                "coleccion_id": row[8], "created_at": row[9]
            }
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad: la colección referenciada no existe"
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar la obra: {str(e)}"
            )
    ```

### 14. `DELETE /artworks/{artwork_id}` (Delete Artwork)
*   **Autenticación:** Sí (HTTP Bearer token)
*   **Parámetros (Path):**
    *   `artwork_id`: integer (requerido)
*   **Respuesta exitosa (JSON):**
    ```json
    { "message": "Obra eliminada exitosamente" }
    ```
*   **Códigos de error:**
    *   `401 Unauthorized`
    *   `404 Not Found`: "Obra no encontrada"
    *   `500 Internal Server Error`
*   **Código de la función:**
    ```python
    @router.delete("/{artwork_id}", status_code=status.HTTP_200_OK)
    async def delete_artwork(
        artwork_id: int,
        current_user: dict = Depends(get_current_user)
    ):
        try:
            with get_db_cursor() as cur:
                cur.execute("SELECT id FROM obras WHERE id = %s", (artwork_id,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Obra no encontrada"
                    )
                cur.execute("DELETE FROM obras WHERE id = %s", (artwork_id,))
            return {"message": "Obra eliminada exitosamente"}
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar la obra: {str(e)}"
            )
    ```

### 15. `POST /artworks/upload` (Upload Image)
*   **Autenticación:** Sí (HTTP Bearer token)
*   **Parámetros (Multipart Form Data):**
    *   `file`: archivo binario (requerido)
*   **Respuesta exitosa (JSON):**
    ```json
    { "imagen_url": "https://res.cloudinary.com/..." }
    ```
*   **Códigos de error:**
    *   `400 Bad Request`: "Tipo de archivo no permitido. Tipos permitidos: .jpg, .jpeg, .png, .webp, .gif"
    *   `401 Unauthorized`
    *   `502 Bad Gateway`: Error de comunicación con la API de Cloudinary
    *   `500 Internal Server Error`
*   **Código de la función:** Ver sección 5.

---

## 4. SEGURIDAD

### Módulo de Seguridad (`security.py`)
```python
from datetime import datetime, timedelta, timezone
from typing import Optional
# Using pyjwt package
import jwt
from passlib.context import CryptContext
from app.config import settings

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a hash from a plain password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
```

---

### Flujo de Autenticación (Login)
1. El usuario envía una petición `POST /auth/login` con su `email` y `password` en texto plano.
2. El endpoint de login busca al usuario en PostgreSQL filtrando por correo electrónico.
3. Si existe, extrae el hash Bcrypt de la base de datos y lo compara con la contraseña introducida mediante `verify_password` de `passlib`.
4. Si las credenciales coinciden, genera un tiempo de expiración (UTC) y codifica un payload que contiene el correo como sujeto (`{"sub": email, "exp": expiration_time}`) firmado con el algoritmo configurado (ej. `HS256`) y la variable `JWT_SECRET_KEY`.
5. El servidor devuelve al cliente el token JWT en formato JSON.
6. El cliente (navegador) almacena este token de forma persistente en su `localStorage` bajo la clave `artfolio_token`.

---

### Validación de Tokens en Peticiones Protegidas (`get_current_user`)
El backend utiliza la dependencia `get_current_user` inyectada en los endpoints que requieren autenticación:
```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to validate JWT tokens and protect private API endpoints.
    Returns the authenticated user details if valid.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión o el token expiró",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    with get_db_cursor() as cur:
        cur.execute("SELECT id, email, created_at FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        if user is None:
            raise credentials_exception
            
    return {"id": user[0], "email": user[1], "created_at": user[2]}
```

---

### Sanitización y Validaciones de Inputs (XSS y Validación de Esquemas)
*   **Librería utilizada:** `nh3` (librería Rust ultrarrápida para Python que previene inyecciones XSS limpiando y removiendo etiquetas HTML).
*   **Estrategia:** Se aplican `field_validator` de Pydantic directamente sobre los campos de entrada de texto.
*   **Campos Protegidos:**
    *   **Colecciones (`CollectionBase`):** Campos `nombre` y `descripcion`.
    *   **Obras (`ArtworkBase`):** Campos `titulo`, `tecnica` y `dimensiones`.

```python
    @field_validator('titulo', 'tecnica', 'dimensiones')
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Prevent XSS: Strips all HTML tags completely, ensuring only plain text remains
        return nh3.clean(v, tags=set())
```

---

### Configuración de CORS
Configurada dinámicamente en `backend/app/main.py` mediante variables de entorno en el arranque:
```python
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
*   **Orígenes permitidos:** Cargados desde la variable `ALLOWED_ORIGINS` (por defecto `http://localhost:5173` en desarrollo, y configurable como comodín `*` o dominios específicos en producción).
*   **Métodos permitidos:** Todos (`["*"]`)
*   **Cabeceras (Headers) permitidas:** Todas (`["*"]`)

---

## 5. SERVICIO DE TERCEROS (Cloudinary)

### Configuración de Inicialización (`init_cloudinary`)
Ubicada en `backend/app/config.py`:
```python
def init_cloudinary():
    """Initialize the Cloudinary SDK with credentials from environment variables."""
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
```

---

### Endpoint `/artworks/upload` Completo
Ubicado en `backend/app/routes/artworks.py`:
```python
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_artwork_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint (Admin-only): Upload an artwork image to Cloudinary.
    Returns the secure HTTPS URL hosted on Cloudinary's CDN.
    """
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    # Extract extension safely even if filename is None
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if f".{ext}" not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(allowed_extensions)}"
        )

    try:
        # Read file contents into memory for Cloudinary upload
        file_bytes = await file.read()

        # Upload to Cloudinary (folder "artfolio" keeps assets organized)
        result = cloudinary.uploader.upload(
            file_bytes,
            folder="artfolio",
            resource_type="image",
            allowed_formats=["jpg", "jpeg", "png", "webp", "gif"]
        )

        secure_url = result.get("secure_url")
        if not secure_url:
            raise ValueError("Cloudinary no devolvió una URL segura en la respuesta")

        return {"imagen_url": secure_url}

    except cloudinary.exceptions.Error as ce:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al comunicarse con Cloudinary: {str(ce)}"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al subir la imagen: {str(e)}"
        )
```

---

### Transformaciones y Parámetros enviados a Cloudinary
*   **Parámetro `folder`:** `"artfolio"` (los archivos se organizan automáticamente en esa carpeta dentro del bucket de Cloudinary).
*   **Parámetro `resource_type`:** `"image"` (restringe la subida únicamente a imágenes).
*   **Formatos permitidos (`allowed_formats`):** `["jpg", "jpeg", "png", "webp", "gif"]`.
*   **Transformaciones aplicadas:** No se configuran transformaciones de redimensionamiento (*resize*), formatos automáticos o reducciones de calidad al subir desde el backend (se sube la imagen original directamente).

---

### Datos devueltos y almacenados
*   **Respuesta de Cloudinary utilizada:** `secure_url` (contiene la URL de acceso seguro `https://res.cloudinary.com/...`).
*   **Datos guardados en PostgreSQL:** Se almacena únicamente la cadena de texto de esta URL segura (`secure_url`) dentro de la columna `imagen_url` de la tabla `obras`. El resto de los metadatos de Cloudinary (public_id, bytes, formato, etc.) se descartan.

---

## 6. FRONTEND

### Listado de Rutas (`router/index.js`)
*   **Ruta:** `/`
    *   **Componente:** `PublicGallery.vue`
    *   **Nombre:** `Gallery`
    *   **Ruta Protegida (Guard):** No
*   **Ruta:** `/login`
    *   **Componente:** `LoginView.vue`
    *   **Nombre:** `Login`
    *   **Ruta Protegida (Guard):** No (Redirige a `/dashboard` si ya hay un token activo).
*   **Ruta:** `/dashboard`
    *   **Componente:** `AdminDashboard.vue`
    *   **Nombre:** `Dashboard`
    *   **Ruta Protegida (Guard):** Sí (`meta: { requiresAuth: true }`). Redirige al login si no se encuentra un token.

---

### Vistas Principales

#### 1. `PublicGallery.vue` (Vista pública)
*   **Consumo de API:**
    *   `GET /collections/` (para listar las carpetas/series de colecciones).
    *   `GET /artworks/` (para listar todas las obras).
*   **Estado Local:**
    *   `theme` ('y2k' o 'gothic'). Persistido en `localStorage.getItem('artfolio_theme')`.
    *   `artworks` (Lista de obras cargadas).
    *   `collections` (Lista de colecciones cargadas).
    *   `searchQuery` (Filtro de búsqueda por texto).
    *   `selectedCollectionId` (Filtro por colección seleccionada).
    *   `selectedArtwork` (Obra seleccionada para abrir la ventana de detalle).
*   **Acciones de Usuario:**
    *   Cambiar de tema estético.
    *   Escribir en el buscador para filtrar obras por título o técnica.
    *   Hacer clic en una colección para filtrar las obras expuestas.
    *   Hacer clic en una obra para abrir una ventana modal con los detalles técnicos de la pieza.

#### 2. `LoginView.vue` (Pantalla de acceso)
*   **Consumo de API:**
    *   `POST /auth/login` (para enviar las credenciales y obtener el JWT).
*   **Estado Local:**
    *   `email` (correo ingresado).
    *   `password` (contraseña ingresada).
    *   `errorMessage` (texto a mostrar en caso de fallo de conexión o credenciales erróneas).
*   **Acciones de Usuario:**
    *   Enviar formulario de acceso (Submit). Redirige a `/dashboard` tras guardar el token.

#### 3. `AdminDashboard.vue` (Panel de administración)
*   **Consumo de API:**
    *   `GET /artworks/` (listar obras del portafolio).
    *   `GET /collections/` (listar colecciones disponibles).
    *   `POST /collections/` (crear una nueva colección).
    *   `POST /artworks/upload` (subir un archivo de imagen a Cloudinary).
    *   `POST /artworks/` (guardar una nueva obra).
    *   `PUT /artworks/{id}` (actualizar una obra existente).
    *   `DELETE /artworks/{id}` (eliminar una obra del inventario).
*   **Estado Local:**
    *   `activeTab` ('obras' o 'colecciones').
    *   `artworks`, `collections`.
    *   `showArtworkModal` (abrir o cerrar modal para añadir/editar obra).
    *   `editingArtwork` (almacena el objeto de la obra que se está editando, o null si es una obra nueva).
    *   `artworkForm` (estructura reactiva con los campos del formulario de la obra).
    *   `collectionForm` (campos para crear una colección).
    *   `uploading` (booleano para bloquear el formulario mientras se sube el archivo a la nube).
*   **Acciones de Usuario:**
    *   Cerrar sesión (borra token del localStorage y redirige a la galería).
    *   Crear colección.
    *   Subir imagen (dispara la carga asíncrona hacia Cloudinary y rellena el input de URL automáticamente).
    *   Añadir o editar obra (Submit de formulario).
    *   Eliminar obra (con ventana de confirmación).

---

### Código Completo de `router/index.js`
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import PublicGallery from '../views/PublicGallery.vue'
import LoginView from '../views/LoginView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Gallery',
    component: PublicGallery
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard to protect dashboard routes
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('artfolio_token')
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next({ name: 'Login' })
    } else {
      next()
    }
  } else {
    // If already logged in, redirect away from Login to Dashboard
    if (to.name === 'Login' && token) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  }
})

export default router
```

---

## 7. PRUEBAS

### Pruebas del Backend (Pytest)

Las pruebas están en la rama `feature/pytest-backend` y constan de 4 archivos de prueba más la configuración de mocks en `conftest.py`.

#### Archivo de Configuración de Mocks: `backend/tests/conftest.py`
```python
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def mock_db_pool():
    """
    Mock patch to prevent database initialization or real connection pool
    creation during tests.
    """
    with patch("app.database.db_pool") as mock_pool, \
         patch("app.database.init_db_pool") as mock_init, \
         patch("app.database.close_db_pool") as mock_close:
        yield mock_pool

@pytest.fixture
def db_cursor():
    """
    Fixture that mocks and yields a database cursor for simulating queries.
    """
    mock_cursor = MagicMock()
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.__exit__.return_value = None
    
    with patch("app.routes.auth.get_db_cursor", return_value=mock_cursor), \
         patch("app.routes.artworks.get_db_cursor", return_value=mock_cursor), \
         patch("app.routes.collections.get_db_cursor", return_value=mock_cursor):
        yield mock_cursor

@pytest.fixture
def client(mock_db_pool):
    """
    Test client for FastAPI integration testing.
    """
    from app.main import app
    with TestClient(app) as test_client:
        yield test_client
```

#### Archivo: `backend/tests/test_main.py`
```python
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to ArtFolio API"}

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

#### Archivo: `backend/tests/test_auth.py`
```python
import pytest
from datetime import datetime

def test_register_success(client, db_cursor):
    db_cursor.fetchone.side_effect = [
        None,
        (1, "test_artist@artfolio.com", datetime.utcnow())
    ]
    
    payload = {"email": "test_artist@artfolio.com", "password": "supersecurepassword"}
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test_artist@artfolio.com"
    assert "id" in data

def test_register_existing_email(client, db_cursor):
    db_cursor.fetchone.return_value = (1,)
    
    payload = {"email": "test_artist@artfolio.com", "password": "supersecurepassword"}
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "El correo electrónico ya está registrado"

def test_login_success(client, db_cursor):
    from app.utils.security import get_password_hash
    hashed_pwd = get_password_hash("artistpassword123")
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", hashed_pwd)
    
    payload = {"email": "artist@artfolio.com", "password": "artistpassword123"}
    response = client.post("/auth/login", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client, db_cursor):
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", "wrong_hash")
    
    payload = {"email": "artist@artfolio.com", "password": "wrongpassword"}
    response = client.post("/auth/login", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"

def test_login_user_not_found(client, db_cursor):
    db_cursor.fetchone.return_value = None
    
    payload = {"email": "notfound@artfolio.com", "password": "somepassword"}
    response = client.post("/auth/login", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"
```

#### Archivo: `backend/tests/test_collections.py`
```python
import pytest
from datetime import datetime
from unittest.mock import patch

def test_get_collections(client, db_cursor):
    db_cursor.fetchall.return_value = [
        (1, "Mitologías Perdidas", "Descripción de mitos", datetime.utcnow()),
        (2, "Anatomía de la Melancolía", "Estudios anatómicos", datetime.utcnow())
    ]
    
    response = client.get("/collections/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre"] == "Mitologías Perdidas"
    assert data[1]["nombre"] == "Anatomía de la Melancolía"

def test_get_collection_by_id_success(client, db_cursor):
    db_cursor.fetchone.return_value = (1, "Mitologías Perdidas", "Descripción de mitos", datetime.utcnow())
    
    response = client.get("/collections/1")
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Mitologías Perdidas"

def test_get_collection_by_id_not_found(client, db_cursor):
    db_cursor.fetchone.return_value = None
    
    response = client.get("/collections/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Colección no encontrada"

def test_create_collection_success(client, db_cursor):
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (10, "Nueva Colección", "Una descripción de prueba", datetime.utcnow())
    ]
    
    headers = {"Authorization": "Bearer fake-token-str"}
    payload = {"nombre": "Nueva Colección", "descripcion": "Una descripción de prueba"}
    
    response = client.post("/collections/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nueva Colección"
    assert data["id"] == 10

def test_update_collection_success(client, db_cursor):
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (10,),
        (10, "Colección Editada", "Descripción editada", datetime.utcnow())
    ]
    
    headers = {"Authorization": "Bearer fake-token-str"}
    payload = {"nombre": "Colección Editada", "descripcion": "Descripción editada"}
    
    response = client.put("/collections/10", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Colección Editada"

def test_delete_collection_success(client, db_cursor):
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (10,)
    ]
    
    headers = {"Authorization": "Bearer fake-token-str"}
    response = client.delete("/collections/10", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Colección eliminada exitosamente"
```

#### Archivo: `backend/tests/test_artworks.py`
```python
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

def test_get_artworks_all(client, db_cursor):
    db_cursor.fetchall.return_value = [
        (1, "Obra 1", "Técnica 1", "100x100 cm", 2024, 500.0, "https://img1.jpg", "Disponible", None, datetime.utcnow()),
        (2, "Obra 2", "Técnica 2", "50x50 cm", 2023, 250.0, "https://img2.jpg", "Vendida", 1, datetime.utcnow())
    ]
    
    response = client.get("/artworks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["titulo"] == "Obra 1"
    assert data[1]["titulo"] == "Obra 2"

def test_get_artwork_by_id_success(client, db_cursor):
    db_cursor.fetchone.return_value = (5, "Obra Específica", "Técnica", "60x60 cm", 2024, 700.00, "https://img.jpg", "Disponible", 2, datetime.utcnow())
    
    response = client.get("/artworks/5")
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Obra Específica"
    assert data["id"] == 5

def test_get_artwork_by_id_not_found(client, db_cursor):
    db_cursor.fetchone.return_value = None
    
    response = client.get("/artworks/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Obra no encontrada"

@patch("cloudinary.uploader.upload")
def test_upload_artwork_image_success(mock_upload, client, db_cursor):
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", datetime.utcnow())
    mock_upload.return_value = {"secure_url": "https://cloudinary/image1.jpg"}
    
    files = {"file": ("test_image.jpg", b"fakeimgdata", "image/jpeg")}
    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/artworks/upload", files=files, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["imagen_url"] == "https://cloudinary/image1.jpg"

def test_upload_artwork_image_invalid_extension(client, db_cursor):
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", datetime.utcnow())
    
    files = {"file": ("malicious_file.exe", b"fakedata", "application/x-msdownload")}
    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/artworks/upload", files=files, headers=headers)
    
    assert response.status_code == 400
    assert "Tipo de archivo no permitido" in response.json()["detail"]

def test_create_artwork_success(client, db_cursor):
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (5,),
        (1, "El Lamento de Ícaro", "Óleo sobre lienzo", "120 x 90 cm", 2024, 1200.00, "https://cloudinary/image1.jpg", "Disponible", 5, datetime.utcnow())
    ]
    
    payload = {
        "titulo": "El Lamento de Ícaro",
        "tecnica": "Óleo sobre lienzo",
        "dimensiones": "120 x 90 cm",
        "ano": 2024,
        "precio": 1200.00,
        "imagen_url": "https://cloudinary/image1.jpg",
        "estado": "Disponible",
        "coleccion_id": 5
    }
    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/artworks/", json=payload, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "El Lamento de Ícaro"
    assert data["precio"] == "1200.00"

def test_create_artwork_invalid_state(client, db_cursor):
    db_cursor.fetchone.return_value = (1, "artist@artfolio.com", datetime.utcnow())
    
    payload = {
        "titulo": "Obra Invalida",
        "tecnica": "Tinta",
        "dimensiones": "10x10 cm",
        "ano": 2024,
        "precio": 100.0,
        "imagen_url": "https://img.jpg",
        "estado": "InvalidoState",
        "coleccion_id": None
    }
    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/artworks/", json=payload, headers=headers)
    
    assert response.status_code == 422

def test_update_artwork_success(client, db_cursor):
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (1,),
        (5,),
        (1, "El Lamento de Ícaro (Editado)", "Óleo sobre lienzo", "120 x 90 cm", 2024, 1300.00, "https://cloudinary/image1.jpg", "Disponible", 5, datetime.utcnow())
    ]
    
    payload = {
        "titulo": "El Lamento de Ícaro (Editado)",
        "tecnica": "Óleo sobre lienzo",
        "dimensiones": "120 x 90 cm",
        "ano": 2024,
        "precio": 1300.00,
        "imagen_url": "https://cloudinary/image1.jpg",
        "estado": "Disponible",
        "coleccion_id": 5
    }
    headers = {"Authorization": "Bearer fake-token"}
    response = client.put("/artworks/1", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "El Lamento de Ícaro (Editado)"

def test_delete_artwork_success(client, db_cursor):
    db_cursor.fetchone.side_effect = [
        (1, "artist@artfolio.com", datetime.utcnow()),
        (1,)
    ]
    
    headers = {"Authorization": "Bearer fake-token"}
    response = client.delete("/artworks/1", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Obra eliminada exitosamente"
```

#### Output de Pytest en la rama de pruebas (100% de éxito)
```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\uta\9-c\desarrollo web integral\y2k edicion\backend
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.12.1, Faker-40.11.0
collected 24 items

tests\test_artworks.py ..........                                        [ 41%]
tests\test_auth.py .....                                                 [ 62%]
tests\test_collections.py .......                                        [ 91%]
tests\test_main.py ..                                                    [100%]
======================= 24 passed, 44 warnings in 1.60s =======================
```

---

### Pruebas del Frontend (Vitest)

#### Archivo: `frontend/tests/LoginView.spec.js`
```javascript
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import LoginView from '../src/views/LoginView.vue'

const mockPush = vi.fn()
const mockRoute = {
  query: { theme: 'y2k' }
}

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => mockRoute
}))

describe('LoginView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    global.fetch = vi.fn()
  })

  it('debe llamar a la API de login al hacer submit con email y contraseña, guardar token y redirigir', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'fake-jwt-token-123' })
    })

    const wrapper = mount(LoginView)

    const emailInput = wrapper.find('#email')
    const passwordInput = wrapper.find('#password')
    await emailInput.setValue('artista@artfolio.com')
    await passwordInput.setValue('artista123')

    await wrapper.find('form').trigger('submit.prevent')

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'artista@artfolio.com', password: 'artista123' })
      })
    )

    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(localStorage.getItem('artfolio_token')).toBe('fake-jwt-token-123')
    expect(mockPush).toHaveBeenCalledWith('/dashboard')
  })

  it('debe mostrar un mensaje de error si el login falla en la respuesta de la API', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Credenciales inválidas' })
    })

    const wrapper = mount(LoginView)

    await wrapper.find('#email').setValue('incorrecto@artfolio.com')
    await wrapper.find('#password').setValue('claveincorrecta')

    await wrapper.find('form').trigger('submit.prevent')

    await new Promise((resolve) => setTimeout(resolve, 50))

    const errorBox = wrapper.find('.error-box-content')
    expect(errorBox.exists()).toBe(true)
    expect(errorBox.text()).toContain('Error de conexión')
  })
})
```

#### Archivo: `frontend/tests/router.spec.js`
```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import router from '../src/router/index.js'

describe('Router Navigation Guards', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('debe bloquear el acceso a /dashboard e ir a /login si no hay token', async () => {
    await router.push('/')
    expect(router.currentRoute.value.path).toBe('/')

    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('Login')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('debe permitir acceder a /dashboard si el token existe en localStorage', async () => {
    localStorage.setItem('artfolio_token', 'token-valido-123')

    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('Dashboard')
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })
})
```

#### Output de Vitest en el frontend (100% de éxito)
```text
 RUN  v4.1.10 C:/uta/9-c/desarrollo web integral/y2k edicion/frontend

 ✓ tests/router.spec.js (2 tests) 10ms
 ✓ tests/LoginView.spec.js (2 tests) 129ms

 Test Files  2 passed (2)
      Tests  4 passed (4)
   Start at  14:50:33
   Duration  2.35s (transform 466ms, setup 0ms, import 787ms, tests 139ms, environment 3.27s)
```

---

## 8. DESPLIEGUE

### Archivo `vercel.json` (Frontend)
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Archivo `render.yaml` (Blueprint de Render)
```yaml
services:
  # 1. Backend Web Service (FastAPI)
  - type: web
    name: artfolio-backend
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: artfolio-db
          property: connectionString
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: JWT_ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "1440"
      - key: HOST
        value: 0.0.0.0
      - key: PORT
        value: "10000"
      - key: CLOUDINARY_CLOUD_NAME
        sync: false
      - key: CLOUDINARY_API_KEY
        sync: false
      - key: CLOUDINARY_API_SECRET
        sync: false
      - key: ALLOWED_ORIGINS
        value: "*"

  # 2. Frontend Static Site (Vue.js + Vite)
  - type: web
    name: artfolio-frontend
    runtime: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://artfolio-backend-px3k.onrender.com

databases:
  - name: artfolio-db
    plan: free
```

---

### Variables de Entorno Requeridas en Producción

#### Para el Backend (Render / Heroku)
1.  `DATABASE_URL`: Connection string de la base de datos de producción (PostgreSQL).
2.  `JWT_SECRET_KEY`: String aleatorio seguro de firma del token JWT.
3.  `JWT_ALGORITHM`: Algoritmo de firma (por defecto: `HS256`).
4.  `ACCESS_TOKEN_EXPIRE_MINUTES`: Minutos de duración del token (por defecto: `1440`).
5.  `CLOUDINARY_CLOUD_NAME`: ID de cuenta de Cloudinary.
6.  `CLOUDINARY_API_KEY`: API Key de Cloudinary.
7.  `CLOUDINARY_API_SECRET`: Secret Key de Cloudinary.
8.  `ALLOWED_ORIGINS`: Dominios del frontend permitidos en CORS.
9.  `PORT` / `HOST`: Puerto (`10000`) y Host (`0.0.0.0`).

#### Para el Frontend (Vercel)
1.  `VITE_API_URL`: Dirección HTTPS pública del Backend en producción (ej. `https://artfolio-backend-px3k.onrender.com`).

---

## 9. CONTROL DE VERSIONES

### Output exacto de `git log --oneline --all`
```text
eb937 docs: create user manual for artist (MANUAL_USUARIO.md)
0bf6b fix(backend): use correct accented status 'En exhibición' in seed_data.py
9b79c fix(backend): replace unicode checkmarks with ASCII [OK] in seed_data.py
5745d fix(backend): allow seed_data.py to read DATABASE_URL from environment
0b6e2 fix(backend): add email-validator to requirements.txt for Pydantic EmailStr support
41cfe fix(deploy): remove plan field from static web service in render.yaml
538dc fix(deploy): use sync: false for manual environment variables in render.yaml
2d642 fix(deploy): use staticPublishPath instead of publishDir in render.yaml
b1948 fix(deploy): change publishPath to publishDir in render.yaml
ac6db feat(frontend): load API_URL from environment variable VITE_API_URL
e4d9d docs: add README-tests.md and update main README with test details
0605b feat(deploy): add deployment configurations for Render, Vercel, Heroku, and Docker
8d809 feat(backend): add comprehensive unit test suite using pytest
4b9c0 docs: add setup, configuration, and execution instructions to README.md
f2288 test: configure pytest for backend and vitest for frontend with unit tests
23c09 feat(backend): implement Cloudinary upload, CORS protection, and input sanitization
f2393 feat(frontend): login gotico al navegar desde seccion gothic
39575 feat(frontend): implementar galeria publica con tema Y2K y selector de temas
c462c feat(frontend): expandir AdminDashboard con CRUD completo de obras
dc638 feat(frontend): redisenar LoginView con estetica Y2K Webcore
3d052 feat(frontend): implementar tema Y2K Webcore y sistema de diseno global
ec2ed feat(backend): mejorar API de obras y startup de la aplicacion
ecf59 fix(backend): corregir encoding de conexion a PostgreSQL en Windows
b0fc3 feat(admin): 🔑 implement login view, inventory dashboard, FAB modal, and CI/CD lint pipeline
7d379 feat(frontend): 🎨 implement public gallery with dark academia and cybersigilism style
```

---

### Output exacto de `git branch -a`
```text
  feature/deploy-config
  feature/pytest-backend
  feature/user-manual
* main
  remotes/origin/feature/deploy-config
  remotes/origin/feature/pytest-backend
  remotes/origin/feature/user-manual
  remotes/origin/main
```

---

### Estado de Pull Requests y Merge a `main`
No se realiza commit directo de características sobre `main`. La integración se controla estrictamente mediante ramas independientes con **Pull Requests** abiertos en GitHub:

1.  **[Pull Request #1 (pytest-backend)](https://github.com/LuisRomo12/artfolio-repo/pull/1):** Para fusionar `feature/pytest-backend` con las pruebas unitarias del backend.
2.  **[Pull Request #2 (deploy-config)](https://github.com/LuisRomo12/artfolio-repo/pull/2):** Para fusionar `feature/deploy-config` con las configuraciones y dependencias del despliegue en la nube.
3.  **[Pull Request #3 (user-manual)](https://github.com/LuisRomo12/artfolio-repo/pull/3):** Para fusionar `feature/user-manual` con el manual en Markdown para el artista.
