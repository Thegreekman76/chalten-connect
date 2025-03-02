# backend\api-gateway\app\core\config.py
import os
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "El Chaltén Connect API Gateway"
    PROJECT_DESCRIPTION: str = "API Gateway para la plataforma integral de turismo en El Chaltén"
    PROJECT_VERSION: str = "0.1.0"
    
    API_V1_STR: str = "/api/v1"
    
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database connection
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "chalten")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "chalten123")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chalten_db")
    
    # Redis connection
    REDIS_SERVER: str = os.getenv("REDIS_SERVER", "localhost")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "redis123")
    
    # Microservices URLs
    USERS_SERVICE_URL: str = os.getenv("USERS_SERVICE_URL", "http://localhost:8001")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "1") == "1"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()