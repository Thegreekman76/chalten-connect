# backend\api-gateway\app\main.py
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
import httpx
import os
import logging

from app.core.config import settings
from app.middlewares.cors import setup_cors
from app.middlewares.logging import setup_logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# NO configurar OAuth2 aquí, se configurará en el router

# Configurar CORS
setup_cors(app)

# Configurar logging middleware
setup_logging(app)

# Configurar cliente HTTP para comunicarse con microservicios
http_client = httpx.AsyncClient(timeout=30.0)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

# Healthcheck endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "api_gateway": "running"}

# Ping endpoint para verificar conectividad con microservicios
@app.get("/ping")
async def ping():
    services_status = {}
    
    # Verificar servicio de usuarios
    try:
        users_url = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")
        response = await http_client.get(f"{users_url}/health")
        if response.status_code == 200:
            services_status["users_service"] = "up"
        else:
            services_status["users_service"] = "down"
    except Exception as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        services_status["users_service"] = "down"
        
    return {
        "status": "ok",
        "api_gateway": "running",
        "services": services_status
    }

# Incluir routers de los diferentes microservicios
from app.routers import users

app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to El Chaltén Connect API",
        "docs": f"{settings.API_V1_STR}/docs"
    }