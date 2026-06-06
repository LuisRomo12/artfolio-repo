from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Token, UserCreate
# Placeholders for now, will implement logic in subsequent tasks
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login():
    """
    Artist authentication endpoint.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login logic is under construction"
    )
