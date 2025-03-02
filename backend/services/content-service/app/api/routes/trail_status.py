# backend\services\content-service\app\api\routes\trail_status.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.trail_status import TrailStatus as TrailStatusModel
from app.models.place import Place as PlaceModel
from app.schemas.trail_status import TrailStatus, TrailStatusCreate, TrailStatusUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=TrailStatus, status_code=status.HTTP_201_CREATED)
def create_trail_status(
    *,
    db: Session = Depends(get_db),
    status_in: TrailStatusCreate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Crear un nuevo registro de estado para un sendero.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == status_in.place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {status_in.place_id} no encontrado"
        )
    
    # Crear el registro de estado
    db_status = TrailStatusModel(
        place_id=status_in.place_id,
        status=status_in.status,
        details=status_in.details,
        valid_until=status_in.valid_until,
        reported_by=current_user_id if status_in.reported_by is None else status_in.reported_by
    )
    
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    
    return db_status

@router.get("/place/{place_id}/current", response_model=TrailStatus)
def get_current_trail_status(
    *,
    db: Session = Depends(get_db),
    place_id: int,
):
    """
    Obtener el estado actual de un sendero específico.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    # Obtener el estado más reciente
    status = db.query(TrailStatusModel)\
        .filter(TrailStatusModel.place_id == place_id)\
        .order_by(TrailStatusModel.last_updated.desc())\
        .first()
    
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay información de estado para el sendero con ID {place_id}"
        )
    
    return status

@router.get("/place/{place_id}/history", response_model=List[TrailStatus])
def get_trail_status_history(
    *,
    db: Session = Depends(get_db),
    place_id: int,
    skip: int = 0,
    limit: int = 10,
):
    """
    Obtener el historial de estados de un sendero específico.
    """
    # Verificar que el lugar existe
    place = db.query(PlaceModel).filter(PlaceModel.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con ID {place_id} no encontrado"
        )
    
    # Obtener el historial de estados
    history = db.query(TrailStatusModel)\
        .filter(TrailStatusModel.place_id == place_id)\
        .order_by(TrailStatusModel.last_updated.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return history

@router.put("/{status_id}", response_model=TrailStatus)
def update_trail_status(
    *,
    db: Session = Depends(get_db),
    status_id: int,
    status_in: TrailStatusUpdate,
    current_user_id: int = Depends(get_current_user),
):
    """
    Actualizar un registro de estado existente.
    """
    status = db.query(TrailStatusModel).filter(TrailStatusModel.id == status_id).first()
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registro de estado con ID {status_id} no encontrado"
        )
    
    # Actualizar campos del registro
    update_data = status_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(status, field, value)
    
    # Actualizar la fecha de última actualización
    status.last_updated = datetime.now()
    
    db.add(status)
    db.commit()
    db.refresh(status)
    
    return status