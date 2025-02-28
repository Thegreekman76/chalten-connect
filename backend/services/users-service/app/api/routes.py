from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging
from typing import Any, List

from app.api.deps import get_db, get_current_active_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.models.user import User
from app.models.profile import Profile
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.schemas.profile import ProfileCreate, ProfileUpdate, Profile as ProfileSchema
from app.schemas.token import Token

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Crear un nuevo usuario en el sistema.
    """
    # Verificar si el email ya existe
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
        
    # Crear el usuario
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        user_type=user_in.user_type,
        is_active=user_in.is_active,
        is_verified=user_in.is_verified
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Crear perfil vacío para el usuario
    profile = Profile(user_id=db_user.id)
    db.add(profile)
    db.commit()
    
    return db_user

@router.get("/", response_model=List[UserSchema])
def read_users(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Obtener lista de usuarios.
    """
    # Solo los administradores pueden ver todos los usuarios
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso insuficiente"
        )
        
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Obtener un usuario por ID.
    """
    # El usuario solo puede ver su propia información a menos que sea admin
    if current_user.id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso insuficiente"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Actualizar un usuario.
    """
    # El usuario solo puede modificar su propia información a menos que sea admin
    if current_user.id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso insuficiente"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    # Actualizar campos
    update_data = user_in.dict(exclude_unset=True)
    
    # Si se proporciona contraseña, actualizar el hash
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Eliminar un usuario.
    """
    # Solo administradores o el propio usuario pueden eliminar
    if current_user.id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso insuficiente"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    # Eliminar el usuario (en cascada se eliminará su perfil)
    db.delete(user)
    db.commit()
    
    return user

@router.post("/login", response_model=Token)
def login_for_access_token(
    *,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, obtiene un token de acceso para credenciales válidas.
    """
    # Buscar el usuario por email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verificar las credenciales
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
        
    # Generar token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
def read_user_me(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Obtener información del usuario actual.
    """
    return current_user

@router.get("/{user_id}/profile", response_model=ProfileSchema)
def read_user_profile(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Obtener perfil de un usuario.
    """
    # El usuario solo puede ver su propio perfil a menos que sea admin
    if current_user.id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso insuficiente"
        )
        
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado"
        )
        
    return profile

@router.put("/{user_id}/profile", response_model=ProfileSchema)
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Actualizar el perfil de un usuario.
    """
    # El usuario solo puede actualizar su propio perfil a menos que sea admin
    if current_user.id != user_id and current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso insuficiente"
        )
        
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado"
        )
        
    # Actualizar campos
    update_data = profile_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile