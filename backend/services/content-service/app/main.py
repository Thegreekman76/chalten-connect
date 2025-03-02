# backend\services\content-service\app\main.py
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.api.deps import get_db

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

# Importar routers (aquí para evitar problemas de importación circular)
from app.api.routes.places import router as places_router
from app.api.routes.categories import router as categories_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.trail_status import router as trail_status_router
from app.api.routes.images import router as images_router

# Registrar routers
app.include_router(places_router, prefix="/places", tags=["places"])
app.include_router(categories_router, prefix="/categories", tags=["categories"])
app.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
app.include_router(trail_status_router, prefix="/trail-status", tags=["trail_status"])
app.include_router(images_router, prefix="/images", tags=["images"])


# Healthcheck endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Verificar que la base de datos esté accesible
        db.execute(text("SELECT 1"))
        return {"status": "ok", "service": "content", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "service": "content", "database": "disconnected"}
        )

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
        "message": "Welcome to El Chaltén Connect Content Service",
        "service": settings.SERVICE_NAME,
        "version": settings.PROJECT_VERSION
    }