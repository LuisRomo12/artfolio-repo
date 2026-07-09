"""
seed_data.py — Populates artfolio_db with:
  - 1 artist user  (artista@artfolio.com / artista123)
  - 2 collections
  - 8 artworks with real Unsplash image URLs
"""
import os, sys, psycopg2
from urllib.parse import urlparse
from passlib.context import CryptContext

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/artfolio_db")
p = urlparse(DATABASE_URL)

conn = psycopg2.connect(
    host=p.hostname, port=p.port,
    user=p.username, password=p.password,
    dbname=p.path.lstrip("/"), client_encoding="UTF8"
)
cur = conn.cursor()

# ── 1. User ──────────────────────────────────────────────────────────────────
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed  = pwd_ctx.hash("artista123")

cur.execute("""
    INSERT INTO usuarios (email, password_hash)
    VALUES ('artista@artfolio.com', %s)
    ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash
""", (hashed,))
print("✓ Usuario artista@artfolio.com creado/actualizado")

# ── 2. Collections ────────────────────────────────────────────────────────────
colecciones = [
    ("Mitologias Perdidas",       "Exploraciones pictorias de mitos olvidados en el tiempo."),
    ("Anatomia de la Melancolia", "Estudios anatomicos y claroscuro de emociones humanas profundas."),
]
for nombre, desc in colecciones:
    cur.execute("""
        INSERT INTO colecciones (nombre, descripcion)
        VALUES (%s, %s)
        ON CONFLICT (nombre) DO NOTHING
    """, (nombre, desc))
print("✓ Colecciones insertadas")

# Fetch IDs
cur.execute("SELECT id, nombre FROM colecciones ORDER BY id")
cols = {row[1]: row[0] for row in cur.fetchall()}
col1 = cols.get("Mitologias Perdidas", 1)
col2 = cols.get("Anatomia de la Melancolia", 2)

# ── 3. Artworks ───────────────────────────────────────────────────────────────
obras = [
    (
        "El Lamento de Icaro",
        "Oleo sobre lienzo",
        "120 x 90 cm", 2024, 1200.00,
        "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?q=80&w=800&auto=format&fit=crop",
        "Disponible", col1
    ),
    (
        "Estudio de las Sombras",
        "Carboncillo sobre papel hecho a mano",
        "40 x 30 cm", 2023, 350.00,
        "https://images.unsplash.com/photo-1579783928621-7a13d66a62d1?q=80&w=800&auto=format&fit=crop",
        "En exhibicion", col2
    ),
    (
        "Memento Mori II",
        "Oleo y pan de oro",
        "80 x 80 cm", 2025, 950.00,
        "https://images.unsplash.com/photo-1580136579312-94651dfd596d?q=80&w=800&auto=format&fit=crop",
        "Vendida", col1
    ),
    (
        "La Camara del Erudito",
        "Acrilico sobre madera",
        "100 x 75 cm", 2024, 800.00,
        "https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?q=80&w=800&auto=format&fit=crop",
        "Disponible", col2
    ),
    (
        "Sinfonia del Crepusculo",
        "Oleo sobre lienzo grueso",
        "150 x 120 cm", 2025, 2400.00,
        "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?q=80&w=800&auto=format&fit=crop",
        "Disponible", col1
    ),
    (
        "Vestigios del Olimpo",
        "Tecnica mixta sobre tela",
        "90 x 90 cm", 2023, 1100.00,
        "https://images.unsplash.com/photo-1569172122301-bc5008bc09c5?q=80&w=800&auto=format&fit=crop",
        "Disponible", col1
    ),
    (
        "Autorretrato con Mascara",
        "Pastel sobre papel Canson",
        "50 x 40 cm", 2024, 480.00,
        "https://images.unsplash.com/photo-1577083552431-6e5fd01988ec?q=80&w=800&auto=format&fit=crop",
        "En exhibicion", col2
    ),
    (
        "Naturaleza Muerta con Luz",
        "Oleo sobre madera entelada",
        "60 x 45 cm", 2022, 620.00,
        "https://images.unsplash.com/photo-1547891654-e66ed7ebb968?q=80&w=800&auto=format&fit=crop",
        "Disponible", col2
    ),
]

for titulo, tecnica, dims, ano, precio, img, estado, col_id in obras:
    cur.execute("""
        INSERT INTO obras (titulo, tecnica, dimensiones, ano, precio, imagen_url, estado, coleccion_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (titulo, tecnica, dims, ano, precio, img, estado, col_id))

conn.commit()
cur.close()
conn.close()
print(f"✓ {len(obras)} obras insertadas en la base de datos")
print("\nListo! Credenciales:")
print("  Email:    artista@artfolio.com")
print("  Password: artista123")
