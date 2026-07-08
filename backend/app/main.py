import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db_pool, close_db_pool
from app.routes import auth, collections, artworks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the PostgreSQL connection pool
    init_db_pool()
    # Ensure static/uploads folder exists
    os.makedirs("static/uploads", exist_ok=True)
    yield
    # Shutdown: Close the PostgreSQL connection pool
    close_db_pool()

app = FastAPI(
    title="ArtFolio API",
    description="CMS Backend for independent visual artists",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(collections.router)
app.include_router(artworks.router)

# Serve uploaded static files (ensure static directory exists beforehand at import-time)
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to ArtFolio API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
