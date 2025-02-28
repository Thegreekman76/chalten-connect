from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Generator, Optional

from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.core.config import settings

# Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/users/login"
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Valida el token JWT y devuelve el usuario actual.
    
    Args:
        db: Sesión de base de datos
        token: Token JWT
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenPayload(sub=user_id)
    except JWTError:
        raise credentials_exception
        
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.id == token_data.sub).first()
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
        
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verifica que el usuario actual esté activo.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Usuario activo
        
    Raises:
        HTTPException: Si el usuario no está activo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user