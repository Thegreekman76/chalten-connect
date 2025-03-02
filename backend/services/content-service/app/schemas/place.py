# backend\services\content-service\app\schemas\place.py
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.place import PlaceType, DifficultyLevel

class CategoryBase(BaseModel):
    """Esquema base para categorías referenciadas desde Place."""
    id: int
    name: str
    slug: str
    
    class Config:
        orm_mode = True  # Esta es la clave

class ImageBase(BaseModel):
    """Esquema base para imágenes referenciadas desde Place."""
    id: int
    url: str
    alt_text: Optional[str] = None
    is_main: bool = False
    
    class Config:
        orm_mode = True 

class PlaceBase(BaseModel):
    """Esquema base para lugares."""
    name: str
    description: str
    short_description: Optional[str] = None
    place_type: str  # Cambiado de PlaceType a str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    difficulty_level: Optional[str] = None  # Cambiado de DifficultyLevel a str
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    elevation_gain_m: Optional[int] = None
    business_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    
    # Validadores para asegurar que los valores string sean los correctos
    @validator('place_type')
    def validate_place_type(cls, v):
        allowed_types = [type.value for type in PlaceType]
        if v not in allowed_types:
            raise ValueError(f'Tipo de lugar inválido. Valores permitidos: {allowed_types}')
        return v
    
    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        if v is not None:
            allowed_levels = [level.value for level in DifficultyLevel]
            if v not in allowed_levels:
                raise ValueError(f'Nivel de dificultad inválido. Valores permitidos: {allowed_levels}')
        return v
    
class PlaceCreate(PlaceBase):
    """Esquema para crear lugares."""
    category_ids: List[int] = []
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('El nombre no puede estar vacío')
        return v
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('La descripción no puede estar vacía')
        return v

class PlaceUpdate(PlaceBase):
    """Esquema para actualizar lugares."""
    name: Optional[str] = None
    description: Optional[str] = None
    place_type: Optional[PlaceType] = None
    category_ids: Optional[List[int]] = None

class PlaceInDBBase(PlaceBase):
    """Esquema base para lugares almacenados en la base de datos."""
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class Place(PlaceInDBBase):
    """Esquema público para lugares."""
    categories: List[CategoryBase] = []
    images: List[ImageBase] = []
    average_rating: Optional[float] = None
    review_count: Optional[int] = None
    trail_status: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True