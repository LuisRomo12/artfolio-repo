import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from typing import List, Optional
from decimal import Decimal
from psycopg2.errors import ForeignKeyViolation
from app.database import get_db_cursor
from app.models import ArtworkResponse, ArtworkCreate
from app.routes.auth import get_current_user

router = APIRouter(prefix="/artworks", tags=["Artworks"])

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

@router.get("/", response_model=List[ArtworkResponse])
async def get_artworks(
    coleccion_id: Optional[int] = Query(None, description="Filtrar obras por ID de colección")
):
    """
    Public endpoint: Retrieve all artworks.
    Optional query parameter 'coleccion_id' filters artworks belonging to that collection.
    """
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

@router.get("/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(artwork_id: int):
    """
    Public endpoint: Retrieve details of a single artwork by ID.
    """
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

@router.post("/", response_model=ArtworkResponse, status_code=status.HTTP_201_CREATED)
async def create_artwork(
    artwork: ArtworkCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint (Admin-only): Register a new artwork in the portfolio.
    Checks and validates status and optional collection existence.
    """
    # Double check state validation in Python logic (redundant to Pydantic and PostgreSQL check constraints)
    valid_states = {"Disponible", "Vendida", "En exhibición"}
    if artwork.estado not in valid_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}"
        )
        
    try:
        with get_db_cursor() as cur:
            # Check if collection exists if provided
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
                    artwork.titulo,
                    artwork.tecnica,
                    artwork.dimensiones,
                    artwork.ano,
                    artwork.precio,
                    artwork.imagen_url,
                    artwork.estado,
                    artwork.coleccion_id
                )
            )
            row = cur.fetchone()
            
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

@router.put("/{artwork_id}", response_model=ArtworkResponse)
async def update_artwork(
    artwork_id: int,
    artwork: ArtworkCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint (Admin-only): Update properties of an existing artwork.
    """
    valid_states = {"Disponible", "Vendida", "En exhibición"}
    if artwork.estado not in valid_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}"
        )
        
    try:
        with get_db_cursor() as cur:
            # Check if artwork exists
            cur.execute("SELECT id FROM obras WHERE id = %s", (artwork_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Obra no encontrada"
                )
            
            # Check if collection exists if provided
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
                    artwork.titulo,
                    artwork.tecnica,
                    artwork.dimensiones,
                    artwork.ano,
                    artwork.precio,
                    artwork.imagen_url,
                    artwork.estado,
                    artwork.coleccion_id,
                    artwork_id
                )
            )
            row = cur.fetchone()
            
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

@router.delete("/{artwork_id}", status_code=status.HTTP_200_OK)
async def delete_artwork(
    artwork_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint (Admin-only): Delete an artwork from the inventory.
    """
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
