from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base

class UserType(str, enum.Enum):
    """Tipos de usuario en el sistema."""
    TOURIST = "tourist"
    BUSINESS = "business"
    ADMIN = "admin"

class User(Base):
    """Modelo para usuarios de la plataforma."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    user_type = Column(Enum(UserType), default=UserType.TOURIST)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    profile = relationship("Profile", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email}>"