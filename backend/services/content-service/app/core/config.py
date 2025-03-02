# backend\services\content-service\app\core\config.py
import os
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    SERVICE_NAME: str = "content-service"
    PROJECT_NAME: str = "El Chaltén Connect Content Service"
    PROJECT_DESCRIPTION: str = "Microservicio de contenido para la plataforma El Chaltén Connect"
    PROJECT_VERSION: str = "0.1.0"
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:3000", "http://localhost:8000"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # JWT configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    JWT_ALGORITHM: str = "HS256"
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @property
    def SQLALCHEMY_DATABASE_URI_VALUE(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        
        POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
        POSTGRES_USER = os.getenv("POSTGRES_USER", "chalten")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "chalten123")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "chalten_db")
        
        return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # Redis configuration
    REDIS_SERVER: str = os.getenv("REDIS_SERVER", "localhost")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "redis123")
    REDIS_URI: str = f"redis://:{REDIS_PASSWORD}@{REDIS_SERVER}:6379/0"
    
    # AWS S3 configuration for media storage
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME: str = os.getenv("AWS_STORAGE_BUCKET_NAME", "chalten-connect")
    AWS_S3_REGION_NAME: str = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
    
    # Maps API configuration
    MAPS_API_KEY: str = os.getenv("MAPS_API_KEY", "")
    MAPS_PROVIDER: str = os.getenv("MAPS_PROVIDER", "mapbox")  # mapbox or google
    
    # Environment configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "1") == "1"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()