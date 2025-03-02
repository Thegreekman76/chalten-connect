# backend\services\users-service\app\schemas\user.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserType

class UserBase(BaseModel):
    """Esquema base para usuarios."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: Optional[UserType] = UserType.TOURIST
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False

class UserCreate(UserBase):
    """Esquema para crear usuarios."""
    email: EmailStr
    password: str
    
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

class UserInDBBase(UserBase):
    """Esquema base para usuarios almacenados en la base de datos."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    """Esquema público para usuarios."""
    pass

class UserInDB(UserInDBBase):
    """Esquema interno para usuarios con hash de contraseña."""
    hashed_password: str