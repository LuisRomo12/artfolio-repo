from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Collection Schemas ---
class CollectionBase(BaseModel):
    nombre: str = Field(..., max_length=255)
    descripcion: Optional[str] = None

class CollectionCreate(CollectionBase):
    pass

class CollectionResponse(CollectionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Artwork Schemas ---
class ArtworkBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    tecnica: str = Field(..., max_length=255)
    dimensiones: str = Field(..., max_length=100)
    ano: int = Field(..., description="Year of creation")
    precio: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    imagen_url: str = Field(..., description="URL or relative path to the uploaded artwork image")
    estado: str = Field(..., pattern="^(Disponible|Vendida|En exhibición)$", description="Must be 'Disponible', 'Vendida', or 'En exhibición'")
    coleccion_id: Optional[int] = None

class ArtworkCreate(ArtworkBase):
    pass

class ArtworkResponse(ArtworkBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
