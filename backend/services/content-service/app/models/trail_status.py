# backend\services\content-service\app\models\trail_status.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base

class StatusType(str, enum.Enum):
    """Estados posibles para los senderos."""
    OPEN = "open"
    PARTIALLY_OPEN = "partially_open"
    CLOSED = "closed"
    MAINTENANCE = "maintenance"
    DANGEROUS = "dangerous"
    UNKNOWN = "unknown"

class TrailStatus(Base):
    """Modelo para el estado actual de los senderos."""
    __tablename__ = "trail_status"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="unknown", nullable=False)  # Cambiado de Enum a String
    details = Column(Text, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    reported_by = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<TrailStatus {self.id} - Place {self.place_id} - Status {self.status}>"