# backend\services\content-service\app\api\routes\categories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.category import Category as CategoryModel
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.utils.slug import create_slug

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user_id: int = Depends(get_current_user),
):
    """ 
    Crear una nueva categoría.
    """
    try:
        # Generar slug único a partir del nombre
        slug = create_slug(category_in.name)
        
        # Verificar si ya existe una categoría con ese slug
        db_category = db.query(CategoryModel).filter(CategoryModel.slug == slug).first()
        if db_category:
            slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Crear la nueva categoría
        db_category = CategoryModel(
            name=category_in.name,
            slug=slug,
            description=category_in.description,
            icon=category_in.icon,
            is_active=category_in.is_active
        )
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        return db_category
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        # Verificar si es un error de unicidad en el nombre
        if "duplicate key value violates unique constraint" in str(e) and "categories_name" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoría con el nombre '{category_in.name}'"
            )
        # Otros errores de integridad
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en la base de datos: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear categoría: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear la categoría"
        )

@router.get("/", response_model=List[Category])
def read_categories(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: bool = True,
):
    """
    Obtener lista de categorías.
    """
    categories = db.query(CategoryModel)\
        .filter(CategoryModel.is_active == is_active)\
        .order_by(CategoryModel.name)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return categories

@router.get("/{category_id}", response_model=Category)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
):
    """
    Obtener una categoría específica por ID.
    """
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada"
        )
    
    return category

@router.get("/slug/{slug}", response_model=Category)
def read_category_by_slug(
    *,
    db: Session = Depends(get_db),
    slug: str,
):
    """
    Obtener una categoría específica por slug.
    """
    category = db.query(CategoryModel).filter(CategoryModel.slug == slug).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con slug '{slug}' no encontrada"
        )
    
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Actualizar una categoría existente.
    """
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada"
        )
    
    # Actualizar campos de la categoría
    update_data = category_in.dict(exclude_unset=True)
    
    # Si se actualiza el nombre, actualizar también el slug
    if "name" in update_data and update_data["name"] != category.name:
        new_slug = create_slug(update_data["name"])
        # Verificar si el nuevo slug ya existe
        slug_exists = db.query(CategoryModel).filter(
            CategoryModel.slug == new_slug, 
            CategoryModel.id != category_id
        ).first()
        
        if slug_exists:
            new_slug = f"{new_slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        update_data["slug"] = new_slug
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user_id: int = Depends(get_current_user),
):
    """
    Eliminar una categoría.
    """
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada"
        )
    
    db.delete(category)
    db.commit()
    
    return None