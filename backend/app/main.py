import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config import settings, init_cloudinary
from app.database import init_db_pool, close_db_pool
from app.routes import auth, collections, artworks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the PostgreSQL connection pool
    init_db_pool()
    # Startup: Initialize Cloudinary SDK
    init_cloudinary()
    yield
    # Shutdown: Close the PostgreSQL connection pool
    close_db_pool()

app = FastAPI(
    title="ArtFolio API",
    description="CMS Backend for independent visual artists",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with secure origin mapping parsed from settings
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(collections.router)
app.include_router(artworks.router)

from fastapi.responses import FileResponse

# Serve uploaded static files (ensure static directory exists beforehand at import-time)
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    if os.path.exists("static/frontend/index.html"):
        return FileResponse("static/frontend/index.html")
    return {"message": "Welcome to ArtFolio API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Serve Vue SPA static assets and client route fallback
if os.path.exists("static/frontend"):
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join("static/frontend", full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("static/frontend/index.html")

