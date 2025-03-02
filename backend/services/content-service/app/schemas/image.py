# backend\services\content-service\app\schemas\image.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImageBase(BaseModel):
    """Esquema base para imágenes."""
    url: str
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    is_main: bool = False
    sort_order: int = 0

class ImageCreate(ImageBase):
    """Esquema para crear imágenes."""
    place_id: int

class ImageUpdate(ImageBase):
    """Esquema para actualizar imágenes."""
    url: Optional[str] = None
    place_id: Optional[int] = None

class Image(ImageBase):
    """Esquema público para imágenes."""
    id: int
    place_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True