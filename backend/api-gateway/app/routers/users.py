# backend\api-gateway\app\routers\users.py
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, Request, status, Path, Body, Header, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr

router = APIRouter()
logger = logging.getLogger(__name__)

# Configurar cliente HTTP para comunicarse con el microservicio de usuarios
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")

# Definir modelos para documentación
class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com", description="Email del usuario")
    first_name: Optional[str] = Field(None, example="John", description="Nombre del usuario")
    last_name: Optional[str] = Field(None, example="Doe", description="Apellido del usuario")
    user_type: Optional[str] = Field("tourist", example="tourist", description="Tipo de usuario (tourist, business, admin)")
    is_active: Optional[bool] = Field(True, description="Indica si el usuario está activo")
    is_verified: Optional[bool] = Field(False, description="Indica si el usuario está verificado")

class UserCreate(UserBase):
    password: str = Field(..., example="password123", description="Contraseña del usuario (mínimo 8 caracteres)")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, example="newemail@example.com", description="Nuevo email")
    first_name: Optional[str] = Field(None, example="NewName", description="Nuevo nombre")
    last_name: Optional[str] = Field(None, example="NewLastName", description="Nuevo apellido")
    password: Optional[str] = Field(None, example="newpassword123", description="Nueva contraseña")
    user_type: Optional[str] = Field(None, example="business", description="Nuevo tipo")
    is_active: Optional[bool] = Field(None, example=True, description="Nuevo estado activo")

class ProfileBase(BaseModel):
    bio: Optional[str] = Field(None, example="Entusiasta de la montaña", description="Biografía o descripción")
    avatar_url: Optional[str] = Field(None, example="https://example.com/avatar.jpg", description="URL del avatar")
    phone: Optional[str] = Field(None, example="+123456789", description="Número de teléfono")
    preferences: Optional[List[str]] = Field(None, example=["adventure", "nature"], description="Preferencias del usuario")
    language: Optional[str] = Field("es", example="es", description="Idioma preferido")

class BusinessProfileUpdate(ProfileBase):
    business_name: Optional[str] = Field(None, example="Hotel Montaña", description="Nombre del negocio")
    business_type: Optional[str] = Field(None, example="hotel", description="Tipo de negocio")
    business_description: Optional[str] = Field(None, example="Hotel con vistas a la montaña", description="Descripción del negocio")
    business_address: Optional[str] = Field(None, example="Calle Principal 123", description="Dirección del negocio")
    business_website: Optional[str] = Field(None, example="https://example.com", description="Sitio web del negocio")
    business_phone: Optional[str] = Field(None, example="+123456789", description="Teléfono del negocio")
    business_email: Optional[EmailStr] = Field(None, example="contact@business.com", description="Email del negocio")

class Token(BaseModel):
    access_token: str
    token_type: str

# Configure OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# Usuarios endpoints
@router.get("/", response_model=List[Dict[str, Any]], summary="Listar usuarios", description="Obtiene una lista de usuarios")
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    token: str = Depends(oauth2_scheme)
):
    """
    Recupera una lista de usuarios.
    
    Requiere autenticación con rol de administrador.
    
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    """
    try:
        # Reenviar la solicitud al microservicio de usuarios
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/",
                params={"skip": skip, "limit": limit},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/me", summary="Perfil del usuario actual", description="Obtiene información del usuario autenticado")
async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    """
    Recupera información del usuario autenticado actual.
    
    Requiere autenticación.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/{user_id}", summary="Obtener usuario", description="Obtiene un usuario específico por ID")
async def get_user(
    user_id: int = Path(..., description="ID del usuario"),
    token: str = Depends(oauth2_scheme)
):
    """
    Recupera un usuario específico por ID.
    
    Requiere autenticación. Solo el propio usuario o un administrador pueden acceder.
    
    - **user_id**: ID único del usuario
    """
    try:
        # Reenviar la solicitud al microservicio de usuarios
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Crear usuario", description="Crea un nuevo usuario")
async def create_user(
    user_data: UserCreate = Body(..., description="Datos del usuario a crear")
):
    """
    Crea un nuevo usuario.
    
    No requiere autenticación.
    """
    try:
        # Reenviar la solicitud al microservicio de usuarios
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USERS_SERVICE_URL}/users/",
                json=user_data.dict()
            )
            
            if response.status_code != 201 and response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/{user_id}", summary="Actualizar usuario", description="Actualiza un usuario existente")
async def update_user(
    user_id: int = Path(..., description="ID del usuario a actualizar"),
    user_data: UserUpdate = Body(..., description="Datos actualizados del usuario"),
    token: str = Depends(oauth2_scheme)
):
    """
    Actualiza un usuario existente.
    
    Requiere autenticación. Solo el propio usuario o un administrador pueden modificar.
    
    - **user_id**: ID del usuario a actualizar
    """
    try:
        # Reenviar la solicitud al microservicio de usuarios
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{USERS_SERVICE_URL}/users/{user_id}",
                json=user_data.dict(exclude_unset=True),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.delete("/{user_id}", summary="Eliminar usuario", description="Elimina un usuario existente")
async def delete_user(
    user_id: int = Path(..., description="ID del usuario a eliminar"),
    token: str = Depends(oauth2_scheme)
):
    """
    Elimina un usuario.
    
    Requiere autenticación. Solo el propio usuario o un administrador pueden eliminar.
    
    - **user_id**: ID del usuario a eliminar
    """
    try:
        # Reenviar la solicitud al microservicio de usuarios
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{USERS_SERVICE_URL}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.post("/login", response_model=Token, summary="Login", description="Autentica un usuario y devuelve un token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autentica a un usuario y devuelve un token de acceso.
    
    - **username**: Email del usuario
    - **password**: Contraseña del usuario
    """
    try:
        # Reenviar la solicitud al microservicio de usuarios
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USERS_SERVICE_URL}/users/login",
                data={"username": form_data.username, "password": form_data.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

# Perfil endpoints
@router.get("/{user_id}/profile", summary="Obtener perfil", description="Obtiene el perfil de un usuario")
async def get_profile(
    user_id: int = Path(..., description="ID del usuario"),
    token: str = Depends(oauth2_scheme)
):
    """
    Obtiene el perfil de un usuario.
    
    Requiere autenticación. Solo el propio usuario o un administrador pueden acceder.
    
    - **user_id**: ID del usuario
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/{user_id}/profile",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@router.put("/{user_id}/profile", summary="Actualizar perfil", description="Actualiza el perfil de un usuario")
async def update_profile(
    user_id: int = Path(..., description="ID del usuario"),
    profile_data: BusinessProfileUpdate = Body(..., description="Datos actualizados del perfil"),
    token: str = Depends(oauth2_scheme)
):
    """
    Actualiza el perfil de un usuario.
    
    Requiere autenticación. Solo el propio usuario o un administrador pueden modificar.
    
    - **user_id**: ID del usuario
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{USERS_SERVICE_URL}/users/{user_id}/profile",
                json=profile_data.dict(exclude_unset=True),
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error from users service: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error from users service")
                )
                
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to users service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )