# backend\services\content-service\app\models\place.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base

# Tabla intermedia para relación muchos a muchos entre lugares y categorías
place_category = Table(
    'place_category',
    Base.metadata,
    Column('place_id', Integer, ForeignKey('places.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# Definimos las enumeraciones para referencia en validaciones
class PlaceType(str, enum.Enum):
    """Tipos de lugares en el sistema."""
    ATTRACTION = "attraction"
    RESTAURANT = "restaurant"
    ACCOMMODATION = "accommodation"
    ACTIVITY = "activity"
    TRAIL = "trail"
    VIEWPOINT = "viewpoint"
    OTHER = "other"

class DifficultyLevel(str, enum.Enum):
    """Niveles de dificultad para senderos y actividades."""
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"
    EXTREME = "extreme"

class Place(Base):
    """Modelo para lugares y puntos de interés."""
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)
    place_type = Column(String, index=True, nullable=False)  # Cambiado de Enum a String
    
    # Ubicación
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    
    # Metadatos
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Para senderos y actividades
    difficulty_level = Column(String, nullable=True)  # Cambiado de Enum a String
    duration_minutes = Column(Integer, nullable=True)
    distance_km = Column(Float, nullable=True)
    elevation_gain_m = Column(Integer, nullable=True)
    
    # Para alojamientos y restaurantes
    business_hours = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    
    # Relaciones
    images = relationship("Image", back_populates="place", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="place", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=place_category, back_populates="places")
    
    def __repr__(self):
        return f"<Place {self.name}>"