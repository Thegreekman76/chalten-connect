from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base

class PreferenceType(str, enum.Enum):
    """Tipos de preferencias para turistas."""
    ADVENTURE = "adventure"
    GASTRONOMY = "gastronomy"
    RELAXATION = "relaxation"
    NATURE = "nature"
    PHOTOGRAPHY = "photography"
    CULTURE = "culture"

class Profile(Base):
    """Modelo para perfiles de usuario con información adicional."""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    preferences = Column(String, nullable=True)  # Almacenado como JSON string
    language = Column(String, default="es")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Para negocios
    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    business_description = Column(Text, nullable=True)
    business_address = Column(String, nullable=True)
    business_website = Column(String, nullable=True)
    business_phone = Column(String, nullable=True)
    business_email = Column(String, nullable=True)
    
    # Relación bidireccional con el usuario
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<Profile {self.id} - User {self.user_id}>"