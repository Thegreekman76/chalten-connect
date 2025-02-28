from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class PreferenceType(str, Enum):
    """Tipos de preferencias para turistas."""
    ADVENTURE = "adventure"
    GASTRONOMY = "gastronomy"
    RELAXATION = "relaxation"
    NATURE = "nature"
    PHOTOGRAPHY = "photography"
    CULTURE = "culture"

class ProfileBase(BaseModel):
    """Esquema base para perfiles de usuario."""
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[List[str]] = None
    language: Optional[str] = "es"
    
    # Campos específicos para negocios
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    business_description: Optional[str] = None
    business_address: Optional[str] = None
    business_website: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None

class ProfileCreate(ProfileBase):
    """Esquema para crear perfiles."""
    user_id: int

class ProfileUpdate(ProfileBase):
    """Esquema para actualizar perfiles."""
    pass

class ProfileSchema(ProfileBase):
    """Esquema público para perfiles."""
    id: int
    user_id: int
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        orm_mode = True