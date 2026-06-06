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
