# backend\services\content-service\app\db\base.py
from sqlalchemy.ext.declarative import declarative_base

# Base para todos los modelos
Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.place import Place
from app.models.category import Category
from app.models.image import Image
from app.models.review import Review
from app.models.trail_status import TrailStatus