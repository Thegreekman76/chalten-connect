# backend\services\content-service\app\models\review.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Review(Base):
    """Modelo para reseñas de lugares."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)  # ID del usuario que hizo la reseña
    rating = Column(Float, nullable=False)  # Valoración (1-5)
    title = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    place = relationship("Place", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review {self.id} - Place {self.place_id} - Rating {self.rating}>"