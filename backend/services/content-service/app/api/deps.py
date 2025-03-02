# backend\services\content-service\app\api\deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Generator, Optional
import httpx
import os

from app.db.session import get_db
from app.schemas.token import TokenPayload
from app.core.config import settings

# Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)

# URL del servicio de usuarios
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> int:
    """
    Valida el token JWT y devuelve el ID del usuario actual.
    
    Args:
        db: Sesión de base de datos
        token: Token JWT
        
    Returns:
        ID del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Hacer una llamada al servicio de usuarios para validar el token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise credentials_exception
                
            user_data = response.json()
            return user_data["id"]
            
    except httpx.RequestError:
        raise credentials_exception