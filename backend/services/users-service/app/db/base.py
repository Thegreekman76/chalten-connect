# backend\services\users-service\app\db\base.py
from sqlalchemy.ext.declarative import declarative_base

# Base para todos los modelos
Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.profile import Profile