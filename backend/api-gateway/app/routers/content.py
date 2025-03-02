# backend\api-gateway\app\routers\content.py
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, Header, Request, status, Query, Path, Body
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)

# Configurar cliente HTTP para comunicarse con el microservicio de contenido
CONTENT_SERVICE_URL = os.getenv("CONTENT_SERVICE_URL", "http://content-service:8002")

# Esquemas para documentación y validación
class CategoryCreate(BaseModel):
    name: str = Field(..., example="Senderos", description="Nombre de la categoría")
    description: Optional[str] = Field(None, example="Rutas de senderismo en El Chaltén", description="Descripción detallada")
    icon: Optional[str] = Field(None, example="hiking", description="Icono representativo")
    is_active: bool = Field(True, description="Indica si la categoría está activa")

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Senderos de montaña", description="Nombre actualizado")
    description: Optional[str] = Field(None, example="Rutas actualizadas", description="Descripción actualizada")
    icon: Optional[str] = Field(None, example="mountain", description="Icono actualizado")
    is_active: Optional[bool] = Field(None, description="Estado actualizado")

class PlaceCreate(BaseModel):
    name: str = Field(..., example="Laguna de los Tres", description="Nombre del lugar")
    description: str = Field(..., example="Hermosa laguna con vistas al Monte Fitz Roy", description="Descripción detallada")
    short_description: Optional[str] = Field(None, example="Vista panorámica del Fitz Roy", description="Descripción corta")
    place_type: str = Field(..., example="trail", description="Tipo de lugar (attraction, restaurant, accommodation, activity, trail, viewpoint, other)")
    latitude: Optional[float] = Field(None, example=-49.2726, description="Coordenada de latitud")
    longitude: Optional[float] = Field(None, example=-72.9723, description="Coordenada de longitud")
    difficulty_level: Optional[str] = Field(None, example="moderate", description="Nivel de dificultad para senderos")
    category_ids: List[int] = Field([], example=[1, 2], description="IDs de categorías asociadas")

class PlaceUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Laguna de los Tres Actualizada", description="Nombre actualizado")
    description: Optional[str] = Field(None, example="Descripción actualizada", description="Descripción actualizada")
    short_description: Optional[str] = Field(None, example="Nueva descripción corta", description="Descripción corta actualizada")
    place_type: Optional[str] = Field(None, example="viewpoint", description="Tipo actualizado")
    is_featured: Optional[bool] = Field(None, example=True, description="Destacar el lugar")
    category_ids: Optional[List[int]] = Field(None, example=[1, 3], description="IDs actualizados de categorías")

class ImageCreate(BaseModel):
    place_id: int = Field(..., example=1, description="ID del lugar al que pertenece la imagen")
    url: str = Field(..., example="https://example.com/image.jpg", description="URL de la imagen")
    alt_text: Optional[str] = Field(None, example="Vista de la Laguna de los Tres", description="Texto alternativo")
    caption: Optional[str] = Field(None, example="Laguna con el Fitz Roy de fondo", description="Leyenda de la imagen")
    is_main: bool = Field(False, example=True, description="Indica si es la imagen principal")

class ImageUpdate(BaseModel):
    url: Optional[str] = Field(None, example="https://example.com/new-image.jpg", description="URL actualizada")
    alt_text: Optional[str] = Field(None, example="Nuevo texto alternativo", description="Texto alternativo actualizado")
    caption: Optional[str] = Field(None, example="Nueva leyenda", description="Leyenda actualizada")
    is_main: Optional[bool] = Field(None, example=True, description="Actualizar estado de imagen principal")

class ReviewCreate(BaseModel):
    place_id: int = Field(..., example=1, description="ID del lugar que se reseña")
    rating: float = Field(..., example=4.5, description="Valoración de 1 a 5")
    title: Optional[str] = Field(None, example="Excelente experiencia", description="Título de la reseña")
    comment: Optional[str] = Field(None, example="Uno de los mejores senderos que he recorrido", description="Comentario detallado")

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, example=5.0, description="Valoración actualizada")
    title: Optional[str] = Field(None, example="Título actualizado", description="Título actualizado")
    comment: Optional[str] = Field(None, example="Comentario actualizado", description="Comentario actualizado")

class TrailStatusCreate(BaseModel):
    place_id: int = Field(..., example=1, description="ID del sendero")
    status: str = Field(..., example="open", description="Estado del sendero (open, partially_open, closed, maintenance, dangerous, unknown)")
    details: Optional[str] = Field(None, example="Sendero abierto. Buenas condiciones.", description="Detalles sobre el estado")
    valid_until: Optional[str] = Field(None, example="2025-03-10T00:00:00Z", description="Hasta cuándo es válido este estado")

class TrailStatusUpdate(BaseModel):
    status: Optional[str] = Field(None, example="partially_open", description="Estado actualizado")
    details: Optional[str] = Field(None, example="Algunas zonas con precauciones por lluvia reciente", description="Detalles actualizados")
    valid_until: Optional[str] = Field(None, example="2025-03-15T00:00:00Z", description="Fecha de validez actualizada")

class ImageReorder(BaseModel):
    image_ids: List[int] = Field(..., example=[3, 1, 2], description="IDs de imágenes en el nuevo orden")

# ============ ENDPOINTS PARA CATEGORÍAS ============

@router.get("/categories/", summary="Listar categorías", description="Obtiene una lista de categorías con filtros opcionales")
async def get_categories(
    skip: int = 0, 
    limit: int = 100,
    is_active: bool = True,
    token: Optional[str] = None
):
    """
    Obtiene una lista de categorías con filtros opcionales.
    
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    - **is_active**: Filtrar solo categorías activas
    """
    try:
        params = {
            "skip": skip,
            "limit": limit,
            "is_active": is_active
        }
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/categories/",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/categories/{category_id}", summary="Obtener categoría", description="Obtiene una categoría específica por ID")
async def get_category(
    category_id: int = Path(..., description="ID de la categoría"),
    token: Optional[str] = None
):
    """
    Obtiene una categoría específica por ID.
    
    - **category_id**: ID único de la categoría
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/categories/{category_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/categories/slug/{slug}", summary="Obtener categoría por slug", description="Obtiene una categoría específica por slug")
async def get_category_by_slug(
    slug: str = Path(..., description="Slug único de la categoría"),
    token: Optional[str] = None
):
    """
    Obtiene una categoría específica por slug.
    
    - **slug**: Slug único de la categoría
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/categories/slug/{slug}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/categories/", summary="Crear categoría", description="Crea una nueva categoría")
async def create_category(
    category_data: CategoryCreate = Body(..., description="Datos de la categoría a crear"),
    token: str = Depends(lambda: Header(...))
):
    """
    Crea una nueva categoría.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONTENT_SERVICE_URL}/categories/",
                json=category_data.dict(),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 201:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/categories/{category_id}", summary="Actualizar categoría", description="Actualiza una categoría existente")
async def update_category(
    category_id: int = Path(..., description="ID de la categoría a actualizar"),
    category_data: CategoryUpdate = Body(..., description="Datos actualizados de la categoría"),
    token: str = Depends(lambda: Header(...))
):
    """
    Actualiza una categoría existente.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CONTENT_SERVICE_URL}/categories/{category_id}",
                json=category_data.dict(exclude_unset=True),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.delete("/categories/{category_id}", summary="Eliminar categoría", description="Elimina una categoría existente")
async def delete_category(
    category_id: int = Path(..., description="ID de la categoría a eliminar"),
    token: str = Depends(lambda: Header(...))
):
    """
    Elimina una categoría existente.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CONTENT_SERVICE_URL}/categories/{category_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 204:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return {"status": "success", "detail": "Category deleted successfully"}
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

# ============ ENDPOINTS PARA LUGARES ============

@router.get("/places/", summary="Listar lugares", description="Obtiene una lista de lugares con filtros opcionales")
async def get_places(
    skip: int = 0, 
    limit: int = 100,
    place_type: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: bool = True,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    token: Optional[str] = None
):
    """
    Obtiene una lista de lugares con filtros opcionales.
    
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    - **place_type**: Filtrar por tipo de lugar
    - **category_id**: Filtrar por categoría
    - **is_active**: Filtrar solo lugares activos
    - **is_featured**: Filtrar lugares destacados
    - **search**: Buscar por texto en nombre o descripción
    """
    try:
        params = {
            "skip": skip,
            "limit": limit,
            "is_active": is_active
        }
        
        if place_type:
            params["place_type"] = place_type
        
        if category_id:
            params["category_id"] = category_id
            
        if is_featured is not None:
            params["is_featured"] = is_featured
            
        if search:
            params["search"] = search
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/places/",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/places/{place_id}", summary="Obtener lugar", description="Obtiene un lugar específico por ID")
async def get_place(
    place_id: int = Path(..., description="ID del lugar"),
    token: Optional[str] = None
):
    """
    Obtiene un lugar específico por ID.
    
    - **place_id**: ID único del lugar
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/places/{place_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/places/slug/{slug}", summary="Obtener lugar por slug", description="Obtiene un lugar específico por slug")
async def get_place_by_slug(
    slug: str = Path(..., description="Slug único del lugar"),
    token: Optional[str] = None
):
    """
    Obtiene un lugar específico por slug.
    
    - **slug**: Slug único del lugar
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/places/slug/{slug}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/places/", summary="Crear lugar", description="Crea un nuevo lugar")
async def create_place(
    place_data: PlaceCreate = Body(..., description="Datos del lugar a crear"),
    token: str = Depends(lambda: Header(...))
):
    """
    Crea un nuevo lugar.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONTENT_SERVICE_URL}/places/",
                json=place_data.dict(),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 201:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/places/{place_id}", summary="Actualizar lugar", description="Actualiza un lugar existente")
async def update_place(
    place_id: int = Path(..., description="ID del lugar a actualizar"),
    place_data: PlaceUpdate = Body(..., description="Datos actualizados del lugar"),
    token: str = Depends(lambda: Header(...))
):
    """
    Actualiza un lugar existente.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CONTENT_SERVICE_URL}/places/{place_id}",
                json=place_data.dict(exclude_unset=True),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.delete("/places/{place_id}", summary="Eliminar lugar", description="Elimina un lugar existente")
async def delete_place(
    place_id: int = Path(..., description="ID del lugar a eliminar"),
    token: str = Depends(lambda: Header(...))
):
    """
    Elimina un lugar existente.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CONTENT_SERVICE_URL}/places/{place_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 204:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return {"status": "success", "detail": "Place deleted successfully"}
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

# ============ ENDPOINTS PARA IMÁGENES ============

@router.get("/images/", summary="Listar imágenes", description="Obtiene una lista de imágenes, opcionalmente filtradas por lugar")
async def get_images(
    skip: int = 0, 
    limit: int = 100,
    place_id: Optional[int] = None,
    token: Optional[str] = None
):
    """
    Obtiene una lista de imágenes, opcionalmente filtradas por lugar.
    
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    - **place_id**: Filtrar por lugar específico
    """
    try:
        params = {
            "skip": skip,
            "limit": limit
        }
        
        if place_id:
            params["place_id"] = place_id
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/images/",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/images/{image_id}", summary="Obtener imagen", description="Obtiene una imagen específica por ID")
async def get_image(
    image_id: int = Path(..., description="ID de la imagen"),
    token: Optional[str] = None
):
    """
    Obtiene una imagen específica por ID.
    
    - **image_id**: ID único de la imagen
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/images/{image_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/images/", summary="Crear imagen", description="Crea una nueva imagen")
async def create_image(
    image_data: ImageCreate = Body(..., description="Datos de la imagen a crear"),
    token: str = Depends(lambda: Header(...))
):
    """
    Crea una nueva imagen.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONTENT_SERVICE_URL}/images/",
                json=image_data.dict(),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 201:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/images/{image_id}", summary="Actualizar imagen", description="Actualiza una imagen existente")
async def update_image(
    image_id: int = Path(..., description="ID de la imagen a actualizar"),
    image_data: ImageUpdate = Body(..., description="Datos actualizados de la imagen"),
    token: str = Depends(lambda: Header(...))
):
    """
    Actualiza una imagen existente.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CONTENT_SERVICE_URL}/images/{image_id}",
                json=image_data.dict(exclude_unset=True),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.delete("/images/{image_id}", summary="Eliminar imagen", description="Elimina una imagen existente")
async def delete_image(
    image_id: int = Path(..., description="ID de la imagen a eliminar"),
    token: str = Depends(lambda: Header(...))
):
    """
    Elimina una imagen existente.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CONTENT_SERVICE_URL}/images/{image_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 204:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return {"status": "success", "detail": "Image deleted successfully"}
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/images/reorder", summary="Reordenar imágenes", description="Reordena las imágenes de un lugar")
async def reorder_images(
    place_id: int = Query(..., description="ID del lugar cuyas imágenes se reordenarán"),
    reorder_data: ImageReorder = Body(..., description="Orden de las imágenes"),
    token: str = Depends(lambda: Header(...))
):
    """
    Reordena las imágenes de un lugar.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CONTENT_SERVICE_URL}/images/reorder?place_id={place_id}",
                json=reorder_data.dict(),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

# ============ ENDPOINTS PARA RESEÑAS ============

@router.get("/reviews/place/{place_id}", summary="Listar reseñas por lugar", description="Obtiene todas las reseñas de un lugar específico")
async def get_place_reviews(
    place_id: int = Path(..., description="ID del lugar"),
    skip: int = 0, 
    limit: int = 100,
    token: Optional[str] = None
):
    """
    Obtiene todas las reseñas de un lugar específico.
    
    - **place_id**: ID del lugar
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    """
    try:
        params = {
            "skip": skip,
            "limit": limit
        }
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/reviews/place/{place_id}",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/reviews/user/me", summary="Mis reseñas", description="Obtiene todas las reseñas del usuario actual")
async def get_my_reviews(
    skip: int = 0, 
    limit: int = 100,
    token: str = Depends(lambda: Header(...))
):
    """
    Obtiene todas las reseñas del usuario actual.
    
    Requiere autenticación.
    
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    """
    try:
        params = {
            "skip": skip,
            "limit": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/reviews/user/me",
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/reviews/{review_id}", summary="Obtener reseña", description="Obtiene una reseña específica por ID")
async def get_review(
    review_id: int = Path(..., description="ID de la reseña"),
    token: Optional[str] = None
):
    """
    Obtiene una reseña específica por ID.
    
    - **review_id**: ID único de la reseña
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/reviews/{review_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/reviews/", summary="Crear reseña", description="Crea una nueva reseña")
async def create_review(
    review_data: ReviewCreate = Body(..., description="Datos de la reseña a crear"),
    token: str = Depends(lambda: Header(...))
):
    """
    Crea una nueva reseña.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONTENT_SERVICE_URL}/reviews/",
                json=review_data.dict(),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 201:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/reviews/{review_id}", summary="Actualizar reseña", description="Actualiza una reseña existente")
async def update_review(
    review_id: int = Path(..., description="ID de la reseña a actualizar"),
    review_data: ReviewUpdate = Body(..., description="Datos actualizados de la reseña"),
    token: str = Depends(lambda: Header(...))
):
    """
    Actualiza una reseña existente.
    
    Requiere autenticación. Solo el autor de la reseña puede actualizarla.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CONTENT_SERVICE_URL}/reviews/{review_id}",
                json=review_data.dict(exclude_unset=True),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.delete("/reviews/{review_id}", summary="Eliminar reseña", description="Elimina una reseña existente")
async def delete_review(
    review_id: int = Path(..., description="ID de la reseña a eliminar"),
    token: str = Depends(lambda: Header(...))
):
    """
    Elimina una reseña existente.
    
    Requiere autenticación. Solo el autor de la reseña puede eliminarla.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CONTENT_SERVICE_URL}/reviews/{review_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 204:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return {"status": "success", "detail": "Review deleted successfully"}
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

# ============ ENDPOINTS PARA ESTADO DE SENDEROS ============

@router.get("/trail-status/place/{place_id}/current", summary="Estado actual del sendero", description="Obtiene el estado actual de un sendero específico")
async def get_current_trail_status(
    place_id: int = Path(..., description="ID del sendero"),
    token: Optional[str] = None
):
    """
    Obtiene el estado actual de un sendero específico.
    
    - **place_id**: ID del sendero
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/trail-status/place/{place_id}/current",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/trail-status/place/{place_id}/history", summary="Historial de estados del sendero", description="Obtiene el historial de estados de un sendero específico")
async def get_trail_status_history(
    place_id: int = Path(..., description="ID del sendero"),
    skip: int = 0,
    limit: int = 10,
    token: Optional[str] = None
):
    """
    Obtiene el historial de estados de un sendero específico.
    
    - **place_id**: ID del sendero
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    """
    try:
        params = {
            "skip": skip,
            "limit": limit
        }
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CONTENT_SERVICE_URL}/trail-status/place/{place_id}/history",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/trail-status/", summary="Crear estado de sendero", description="Crea un nuevo registro de estado para un sendero")
async def create_trail_status(
    status_data: TrailStatusCreate = Body(..., description="Datos del estado del sendero a crear"),
    token: str = Depends(lambda: Header(...))
):
    """
    Crea un nuevo registro de estado para un sendero.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONTENT_SERVICE_URL}/trail-status/",
                json=status_data.dict(),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 201:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/trail-status/{status_id}", summary="Actualizar estado de sendero", description="Actualiza un registro de estado de sendero existente")
async def update_trail_status(
    status_id: int = Path(..., description="ID del estado de sendero a actualizar"),
    status_data: TrailStatusUpdate = Body(..., description="Datos actualizados del estado del sendero"),
    token: str = Depends(lambda: Header(...))
):
    """
    Actualiza un registro de estado de sendero existente.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CONTENT_SERVICE_URL}/trail-status/{status_id}",
                json=status_data.dict(exclude_unset=True),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from content service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from content service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to content service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )