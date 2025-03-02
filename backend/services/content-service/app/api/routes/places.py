# backend\services\content-service\app\api\routes\places.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.place import Place as PlaceModel
from app.models.category import Category as CategoryModel
from app.models.image import Image as ImageModel
from app.models.review import Review as ReviewModel
from app.schemas.place import Place, PlaceCreate, PlaceUpdate
from app.schemas.image import Image, ImageCreate
from app.utils.slug import create_slug

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Place, status_code=status.HTTP_201_CREATED)
def create_place(
    *,
    db: Session = Depends(get_db),
    place_in: PlaceCreate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Crear un nuevo lugar.
    """
    # Generar slug único a partir del nombre
    slug = create_slug(place_in.name)
    
    # Verificar si ya existe un lugar con ese slug
    db_place = db.query(PlaceModel).filter(PlaceModel.slug == slug).first()
    if db_place:
        slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Crear el nuevo lugar
    db_place = PlaceModel(
        name=place_in.name,
        slug=slug,
        description=place_in.description,
        short_description=place_in.short_description,
        place_type=place_in.place_type,
        latitude=place_in.latitude,
        longitude=place_in.longitude,
        address=place_in.address,
        is_active=place_in.is_active,
        is_featured=place_in.is_featured,
        difficulty_level=place_in.difficulty_level,
        duration_minutes=place_in.duration_minutes,
        distance_km=place_in.distance_km,
        elevation_gain_m=place_in.elevation_gain_m,
        business_hours=place_in.business_hours,
        contact_phone=place_in.contact_phone,
        contact_email=place_in.contact_email,
        website=place_in.website,
    )
    
    # Asociar categorías
    if place_in.category_ids:
        categories = db.query(CategoryModel).filter(CategoryModel.id.in_(place_in.category_ids)).all()
        db_place.categories = categories
    
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    
    return db_place

@router.get("/", response_model=List[Place])
def read_places(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    place_type: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: bool = True,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
):
    """
    Obtener lista de lugares con filtros opcionales.
    """
    query = db.query(PlaceModel).filter(PlaceModel.is_active == is_active)
    
    # Aplicar filtros si se proporcionan
    if place_type:
        query = query.filter(PlaceModel.place_type == place_type)
    
    if category_id:
        query = query.join(PlaceModel.categories).filter(CategoryModel.id == category_id)
    
    if is_featured is not None:
        query = query.filter(PlaceModel.is_featured == is_featured)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            PlaceModel.name.ilike(search_term) | 
            PlaceModel.description.ilike(search_term) |
            PlaceModel.short_description.ilike(search_term)
        )
    
    # Ordenar por nombre
    query = query.order_by(PlaceModel.name)
    
    # Aplicar paginación
    places = query.offset(skip).limit(limit).all()
    
    # Para cada lugar, asegurarse de que las relaciones estén cargadas
    result = []
    for place in places:
        # Calcular valoraciones medias y número de reseñas
        avg_query = db.query(func.avg(ReviewModel.rating)).filter(ReviewModel.place_id == place.id)
        avg_rating = avg_query.scalar()
        setattr(place, "average_rating", float(avg_rating) if avg_rating else None)
        
        # Contar número de reseñas
        count_query = db.query(func.count(ReviewModel.id)).filter(ReviewModel.place_id == place.id)
        review_count = count_query.scalar()
        setattr(place, "review_count", review_count)
        
        # Asegurarse de que las relaciones estén cargadas (eager loading)
        db.refresh(place)
        result.append(place)
    
    return result

@router.get("/{place_id}", response_model=Place)
def read_place(
    *,
    db: Session = Depends(get_db),
    place_id: int,
):
    """
    Obtener un lugar específico por ID.
    """
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    # Calcular media de valoraciones
    avg_query = db.query(func.avg(ReviewModel.rating)).filter(ReviewModel.place_id == place.id)
    avg_rating = avg_query.scalar()
    setattr(place, "average_rating", float(avg_rating) if avg_rating else None)
    
    # Contar número de reseñas
    count_query = db.query(func.count(ReviewModel.id)).filter(ReviewModel.place_id == place.id)
    review_count = count_query.scalar()
    setattr(place, "review_count", review_count)
    
    # Aseguramos que las relaciones estén cargadas
    db.refresh(place)
    
    return place

@router.get("/slug/{slug}", response_model=Place)
def read_place_by_slug(
    *,
    db: Session = Depends(get_db),
    slug: str,
):
    """
    Obtener un lugar específico por slug.
    """
    place = db.query(PlaceModel).filter(PlaceModel.slug == slug).first()
    
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con slug '{slug}' no encontrado"
        )
    
    # Calcular media de valoraciones
    avg_query = db.query(func.avg(ReviewModel.rating)).filter(ReviewModel.place_id == place.id)
    avg_rating = avg_query.scalar()
    setattr(place, "average_rating", float(avg_rating) if avg_rating else None)
    
    # Contar número de reseñas
    count_query = db.query(func.count(ReviewModel.id)).filter(ReviewModel.place_id == place.id)
    review_count = count_query.scalar()
    setattr(place, "review_count", review_count)
    
    return place

@router.put("/{place_id}", response_model=Place)
def update_place(
    *,
    db: Session = Depends(get_db),
    place_id: int,
    place_in: PlaceUpdate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Actualizar un lugar existente.
    """
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    # Actualizar campos del lugar
    update_data = place_in.dict(exclude_unset=True)
    
    # Manejar categorías separadamente si están presentes
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        if category_ids is not None:
            categories = db.query(CategoryModel).filter(CategoryModel.id.in_(category_ids)).all()
            place.categories = categories
    
    # Actualizar el resto de campos
    for field, value in update_data.items():
        setattr(place, field, value)
    
    db.add(place)
    db.commit()
    db.refresh(place)
    
    return place

@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(
    *,
    db: Session = Depends(get_db),
    place_id: int,
    current_user_id: int = Depends(get_current_user),
):
    """
    Eliminar un lugar.
    """
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    db.delete(place)
    db.commit()
    
    return None

@router.post("/{place_id}/images", response_model=Image)
def upload_place_image(
    *,
    db: Session = Depends(get_db),
    place_id: int,
    image_in: ImageCreate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Subir una nueva imagen para un lugar.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    # Si la imagen se marca como principal, desmarcar las demás
    if image_in.is_main:
        db.query(ImageModel).filter(
            ImageModel.place_id == place_id,
            ImageModel.is_main == True
        ).update({"is_main": False})
    
    # Crear la imagen
    db_image = ImageModel(
        place_id=place_id,
        url=image_in.url,
        alt_text=image_in.alt_text,
        caption=image_in.caption,
        is_main=image_in.is_main,
        sort_order=image_in.sort_order
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image