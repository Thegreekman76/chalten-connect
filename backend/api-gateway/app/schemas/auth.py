from pydantic import BaseModel

class LoginRequest(BaseModel):
    """Esquema para solicitud de login"""
    username: str
    password: str