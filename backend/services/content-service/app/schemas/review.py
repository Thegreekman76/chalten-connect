# backend\services\content-service\app\schemas\review.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    """Esquema base para reseñas."""
    rating: float
    title: Optional[str] = None
    comment: Optional[str] = None

    @validator('rating')
    def rating_must_be_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError('La valoración debe estar entre 1 y 5')
        return v

class ReviewCreate(ReviewBase):
    """Esquema para crear reseñas."""
    place_id: int

class ReviewUpdate(ReviewBase):
    """Esquema para actualizar reseñas."""
    rating: Optional[float] = None

class Review(ReviewBase):
    """Esquema público para reseñas."""
    id: int
    place_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True