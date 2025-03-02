# backend\services\content-service\app\schemas\category.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PlaceInDBBase(BaseModel):
    """Esquema base simplificado para lugares referenciados desde categorías."""
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    """Esquema base para categorías."""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True

class CategoryCreate(CategoryBase):
    """Esquema para crear categorías."""
    pass

class CategoryUpdate(CategoryBase):
    """Esquema para actualizar categorías."""
    name: Optional[str] = None

class Category(CategoryBase):
    """Esquema público para categorías."""
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class CategoryWithPlaces(Category):
    """Categoría con lista de lugares asociados."""
    places: List[PlaceInDBBase] = []