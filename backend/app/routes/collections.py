from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import CollectionResponse, CollectionCreate

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get("/", response_model=List[CollectionResponse])
async def get_collections():
    """
    Public access to retrieve all collections.
    """
    return []

@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(collection: CollectionCreate):
    """
    Admin-only endpoint to create a new collection.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Create collection logic is under construction"
    )
