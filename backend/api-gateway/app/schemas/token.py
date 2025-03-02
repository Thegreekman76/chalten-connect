# backend\api-gateway\app\schemas\token.py
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """Esquema para respuesta de token de autenticación."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Esquema para el payload del token JWT."""
    sub: Optional[str] = None