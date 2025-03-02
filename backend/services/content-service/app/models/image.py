# backend\services\content-service\app\models\image.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Image(Base):
    """Modelo para imágenes asociadas a lugares."""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    alt_text = Column(String, nullable=True)
    caption = Column(Text, nullable=True)
    is_main = Column(Boolean, default=False)  # Imagen principal del lugar
    sort_order = Column(Integer, default=0)  # Orden de visualización
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    place = relationship("Place", back_populates="images")
    
    def __repr__(self):
        return f"<Image {self.id} - Place {self.place_id}>"