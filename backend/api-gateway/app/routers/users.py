# backend\api-gateway\app\routers\users.py
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
from typing import List, Dict, Any, Optional

from app.schemas.user import UserCreate, UserUpdate, UserSchema
from app.schemas.token import Token

logger = logging.getLogger(__name__)

router = APIRouter()

# Configurar OAuth2 específicamente para este router
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# Configurar cliente HTTP para comunicarse con el microservicio de usuarios
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")

@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    token: str = Depends(oauth2_scheme)
):
    """
    Recupera una lista de usuarios.
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

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    token: str = Depends(oauth2_scheme)
):
    """
    Recupera un usuario específico por ID.
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

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate
):
    """
    Crea un nuevo usuario.
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

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    token: str = Depends(oauth2_scheme)
):
    """
    Actualiza un usuario existente.
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

@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(
    user_id: int,
    token: str = Depends(oauth2_scheme)
):
    """
    Elimina un usuario.
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

@router.post("/login", response_model=Token)
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