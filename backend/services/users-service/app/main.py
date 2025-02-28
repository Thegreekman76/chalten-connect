from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.api.deps import get_db
from app.api.routes import router as api_router

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Verificar que la base de datos esté accesible
        db.execute("SELECT 1")
        return {"status": "ok", "service": "users", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "service": "users", "database": "disconnected"}
        )

# Incluir rutas de la API
app.include_router(api_router, prefix="/users")

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
        "message": "Welcome to El Chaltén Connect Users Service",
        "service": settings.SERVICE_NAME,
        "version": settings.PROJECT_VERSION
    }