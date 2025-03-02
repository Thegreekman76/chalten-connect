# backend\services\users-service\app\schemas\profile.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from app.models.profile import PreferenceType

class ProfileBase(BaseModel):
    """Esquema base para perfiles de usuario."""
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[List[PreferenceType]] = None
    language: Optional[str] = "es"
    
    # Campos específicos para negocios
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    business_description: Optional[str] = None
    business_address: Optional[str] = None
    business_website: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[EmailStr] = None

class ProfileCreate(ProfileBase):
    """Esquema para crear perfiles."""
    user_id: int

class ProfileUpdate(ProfileBase):
    """Esquema para actualizar perfiles."""
    pass

class Profile(ProfileBase):
    """Esquema público para perfiles."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True