from typing import Optional
from pydantic import BaseModel, validator
from enum import Enum

class UserType(str, Enum):
    TOURIST = "tourist"
    BUSINESS = "business"
    ADMIN = "admin"

class UserBase(BaseModel):
    """Esquema base para usuarios."""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: Optional[UserType] = UserType.TOURIST
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False

class UserCreate(UserBase):
    """Esquema para crear usuarios."""
    email: str
    password: str
    
    @validator('email')
    def email_format(cls, v):
        if '@' not in v:
            raise ValueError('Correo electrónico inválido')
        return v
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserUpdate(UserBase):
    """Esquema para actualizar usuarios."""
    password: Optional[str] = None
    
    @validator('password')
    def password_min_length(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserSchema(BaseModel):
    """Esquema público para usuarios."""
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        orm_mode = True