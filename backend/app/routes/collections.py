from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from psycopg2.errors import UniqueViolation
from app.database import get_db_cursor
from app.models import CollectionResponse, CollectionCreate
from app.routes.auth import get_current_user

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get("/", response_model=List[CollectionResponse])
async def get_collections():
    """
    Public endpoint: Retrieve all collections, ordered alphabetically by name.
    """
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

@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: int):
    """
    Public endpoint: Retrieve details of a single collection by ID.
    """
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

@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection: CollectionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint (Admin-only): Create a new conceptual collection.
    """
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

@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    collection: CollectionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint (Admin-only): Update an existing collection name and description.
    """
    try:
        with get_db_cursor() as cur:
            # Check existence first
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

@router.delete("/{collection_id}", status_code=status.HTTP_200_OK)
async def delete_collection(
    collection_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected endpoint (Admin-only): Delete an existing collection.
    Associated artworks will have their collection_id set to NULL automatically.
    """
    try:
        with get_db_cursor() as cur:
            # Check existence
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
