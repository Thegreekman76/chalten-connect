# backend\services\content-service\app\api\routes\images.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.api.deps import get_db, get_current_user
from app.models.image import Image as ImageModel
from app.models.place import Place as PlaceModel
from app.schemas.image import Image, ImageCreate, ImageUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Image])
def read_images(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    place_id: Optional[int] = None
):
    """
    Obtener lista de imágenes, opcionalmente filtradas por lugar.
    """
    query = db.query(ImageModel)
    
    if place_id:
        query = query.filter(ImageModel.place_id == place_id)
    
    images = query.order_by(ImageModel.sort_order).offset(skip).limit(limit).all()
    return images

@router.get("/{image_id}", response_model=Image)
def read_image(
    *,
    db: Session = Depends(get_db),
    image_id: int
):
    """
    Obtener una imagen específica por ID.
    """
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagen con ID {image_id} no encontrada"
        )
    
    return image

@router.post("/", response_model=Image, status_code=status.HTTP_201_CREATED)
def create_image(
    *,
    db: Session = Depends(get_db),
    image_in: ImageCreate,
    current_user_id: int = Depends(get_current_user)
):
    """
    Crear una nueva imagen.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == image_in.place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {image_in.place_id} no encontrado"
        )
    
    # Si la imagen se marca como principal, desmarcar las demás
    if image_in.is_main:
        db.query(ImageModel).filter(
            ImageModel.place_id == image_in.place_id,
            ImageModel.is_main == True
        ).update({"is_main": False})
    
    # Crear la imagen
    db_image = ImageModel(
        place_id=image_in.place_id,
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

@router.put("/{image_id}", response_model=Image)
def update_image(
    *,
    db: Session = Depends(get_db),
    image_id: int,
    image_in: ImageUpdate,
    current_user_id: int = Depends(get_current_user)
):
    """
    Actualizar una imagen existente.
    """
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagen con ID {image_id} no encontrada"
        )
    
    # Verificar si se está cambiando el place_id
    if image_in.place_id is not None and image_in.place_id != image.place_id:
        # Verificar que el nuevo lugar existe
        place = db.query(PlaceModel).filter(PlaceModel.id == image_in.place_id).first()
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lugar con ID {image_in.place_id} no encontrado"
            )
    
    # Si se está cambiando el estado de is_main a True
    if image_in.is_main and not image.is_main:
        # Desmarcar otras imágenes como principales
        db.query(ImageModel).filter(
            ImageModel.place_id == (image_in.place_id or image.place_id),
            ImageModel.id != image_id,
            ImageModel.is_main == True
        ).update({"is_main": False})
    
    # Actualizar campos de la imagen
    update_data = image_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(image, field, value)
    
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return image

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    *,
    db: Session = Depends(get_db),
    image_id: int,
    current_user_id: int = Depends(get_current_user)
):
    """
    Eliminar una imagen.
    """
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagen con ID {image_id} no encontrada"
        )
    
    db.delete(image)
    db.commit()
    
    return None

@router.put("/reorder", response_model=List[Image])
def reorder_images(
    *,
    db: Session = Depends(get_db),
    place_id: int,
    image_ids: List[int],
    current_user_id: int = Depends(get_current_user)
):
    """
    Reordenar las imágenes de un lugar.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    # Verificar que todos los IDs corresponden a imágenes del lugar
    images = db.query(ImageModel).filter(
        ImageModel.place_id == place_id,
        ImageModel.id.in_(image_ids)
    ).all()
    
    if len(images) != len(image_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Algunos IDs de imágenes no son válidos o no pertenecen a este lugar"
        )
    
    # Actualizar el orden de las imágenes
    for index, image_id in enumerate(image_ids):
        db.query(ImageModel).filter(ImageModel.id == image_id).update(
            {"sort_order": index}
        )
    
    db.commit()
    
    # Obtener las imágenes actualizadas en el nuevo orden
    updated_images = db.query(ImageModel).filter(
        ImageModel.place_id == place_id
    ).order_by(ImageModel.sort_order).all()
    
    return updated_images