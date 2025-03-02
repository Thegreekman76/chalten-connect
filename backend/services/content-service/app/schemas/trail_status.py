# backend\services\content-service\app\schemas\trail_status.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.trail_status import StatusType

class TrailStatusBase(BaseModel):
    """Esquema base para estados de senderos."""
    status: str  # Cambiado de StatusType a str
    details: Optional[str] = None
    valid_until: Optional[datetime] = None
    
    # Validador para asegurar que los valores string sean los correctos
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = [status.value for status in StatusType]
        if v not in allowed_statuses:
            raise ValueError(f'Estado inválido. Valores permitidos: {allowed_statuses}')
        return v

class TrailStatusCreate(TrailStatusBase):
    """Esquema para crear estados de senderos."""
    place_id: int
    reported_by: Optional[int] = None

class TrailStatusUpdate(TrailStatusBase):
    """Esquema para actualizar estados de senderos."""
    status: Optional[StatusType] = None

class TrailStatus(TrailStatusBase):
    """Esquema público para estados de senderos."""
    id: int
    place_id: int
    last_updated: datetime
    reported_by: Optional[int] = None
    
    class Config:
        orm_mode = True