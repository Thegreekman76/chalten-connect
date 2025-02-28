from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.core.config import settings

# Crear el motor de base de datos
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI_VALUE,
    # Configuraciones para conexiones
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    pool_recycle=3600,   # Recicla las conexiones cada hora
    echo=settings.DEBUG  # Mostrar consultas SQL en modo debug
)

# Crear fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """
    Genera una sesión de base de datos para el contexto actual.
    Se encarga de cerrar la sesión al finalizar.
    
    Yields:
        Objeto de sesión SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()