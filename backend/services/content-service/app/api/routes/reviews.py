# backend\services\content-service\app\api\routes\reviews.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.api.deps import get_db, get_current_user
from app.models.review import Review as ReviewModel
from app.models.place import Place as PlaceModel
from app.schemas.review import Review, ReviewCreate, ReviewUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(
    *,
    db: Session = Depends(get_db),
    review_in: ReviewCreate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Crear una nueva reseña.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == review_in.place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {review_in.place_id} no encontrado"
        )
    
    # Verificar si el usuario ya ha dejado una reseña para este lugar
    existing_review = db.query(ReviewModel).filter(
        ReviewModel.place_id == review_in.place_id,
        ReviewModel.user_id == current_user_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya has dejado una reseña para este lugar"
        )
    
    # Crear la reseña
    db_review = ReviewModel(
        place_id=review_in.place_id,
        user_id=current_user_id,
        rating=review_in.rating,
        title=review_in.title,
        comment=review_in.comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review

@router.get("/place/{place_id}", response_model=List[Review])
def read_place_reviews(
    *,
    db: Session = Depends(get_db),
    place_id: int,
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtener todas las reseñas de un lugar específico.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    reviews = db.query(ReviewModel)\
        .filter(ReviewModel.place_id == place_id)\
        .order_by(ReviewModel.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return reviews

@router.get("/user/me", response_model=List[Review])
def read_my_reviews(
    *,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtener todas las reseñas del usuario actual.
    """
    reviews = db.query(ReviewModel)\
        .filter(ReviewModel.user_id == current_user_id)\
        .order_by(ReviewModel.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return reviews

@router.get("/{review_id}", response_model=Review)
def read_review(
    *,
    db: Session = Depends(get_db),
    review_id: int,
):
    """
    Obtener una reseña específica por ID.
    """
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reseña con ID {review_id} no encontrada"
        )
    
    return review

@router.put("/{review_id}", response_model=Review)
def update_review(
    *,
    db: Session = Depends(get_db),
    review_id: int,
    review_in: ReviewUpdate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Actualizar una reseña existente.
    """
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reseña con ID {review_id} no encontrada"
        )
    
    # Verificar que el usuario es el autor de la reseña
    if review.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta reseña"
        )
    
    # Actualizar campos de la reseña
    update_data = review_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    *,
    db: Session = Depends(get_db),
    review_id: int,
    current_user_id: int = Depends(get_current_user),
):
    """
    Eliminar una reseña.
    """
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reseña con ID {review_id} no encontrada"
        )
    
    # Verificar que el usuario es el autor de la reseña
    if review.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta reseña"
        )
    
    db.delete(review)
    db.commit()
    
    return None