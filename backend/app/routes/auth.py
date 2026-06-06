from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import timedelta
from app.config import settings
from app.database import get_db_cursor
from app.models import Token, UserCreate, UserResponse
from app.utils.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to validate JWT tokens and protect private API endpoints.
    Returns the authenticated user details if valid.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión o el token expiró",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    with get_db_cursor() as cur:
        cur.execute("SELECT id, email, created_at FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        if user is None:
            raise credentials_exception
            
    return {"id": user[0], "email": user[1], "created_at": user[2]}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Registers a new artist profile.
    """
    hashed_pwd = get_password_hash(user.password)
    
    try:
        with get_db_cursor() as cur:
            # Check if user already exists
            cur.execute("SELECT id FROM usuarios WHERE email = %s", (user.email,))
            if cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está registrado"
                )
            
            # Insert new user
            cur.execute(
                "INSERT INTO usuarios (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at",
                (user.email, hashed_pwd)
            )
            new_user = cur.fetchone()
            
        return {
            "id": new_user[0],
            "email": new_user[1],
            "created_at": new_user[2]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserCreate):
    """
    Validates user credentials against PostgreSQL and returns a signed JWT access token.
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT id, email, password_hash FROM usuarios WHERE email = %s", (credentials.email,))
            user = cur.fetchone()
            
        if not user or not verify_password(credentials.password, user[2]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user[1]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servidor durante el login: {str(e)}"
        )
