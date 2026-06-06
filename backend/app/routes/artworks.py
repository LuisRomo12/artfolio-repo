from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.models import ArtworkResponse, ArtworkCreate

router = APIRouter(prefix="/artworks", tags=["Artworks"])

@router.get("/", response_model=List[ArtworkResponse])
async def get_artworks(
    coleccion_id: Optional[int] = Query(None, description="Filter artworks by collection ID")
):
    """
    Public access to retrieve all artworks, optionally filtered by collection.
    """
    return []

@router.post("/", response_model=ArtworkResponse, status_code=status.HTTP_201_CREATED)
async def create_artwork(artwork: ArtworkCreate):
    """
    Admin-only endpoint to create a new artwork.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Create artwork logic is under construction"
    )
