# test_simplified.py - Script específico para probar lugares, imágenes, reseñas y estados de senderos
import httpx
import asyncio
import json
import random
import string
from typing import Dict, Any, Optional
import logging
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("content-service-test")

# URLs
CONTENT_SERVICE_URL = "http://localhost:8002"
API_GATEWAY_URL = "http://localhost:8000/api/v1"

# Token de autenticación
AUTH_TOKEN = None

def generate_random_string(length=6):
    """Genera una cadena aleatoria para evitar colisiones."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Datos simplificados para pruebas
test_user = {
    "email": f"test{generate_random_string()}@chalten.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
}

# Datos simplificados para pruebas
simple_place = {
    "name": f"Laguna de los Tres {generate_random_string()}",
    "description": "Hermosa laguna con vistas al Monte Fitz Roy",
    "short_description": "Vista panorámica del Fitz Roy",
    "place_type": "trail",  # String simple en lugar de enum
    "is_active": True
}

simple_image = {
    "url": "https://example.com/image.jpg",
    "alt_text": "Vista de la Laguna de los Tres",
    "is_main": True
}

simple_review = {
    "rating": 4.5,
    "title": "Excelente experiencia",
    "comment": "Uno de los mejores senderos que he recorrido"
}

simple_trail_status = {
    "status": "open",
    "details": "Sendero abierto. Buenas condiciones."
}

# Obtener token
async def get_auth_token():
    global AUTH_TOKEN
    if AUTH_TOKEN:
        return AUTH_TOKEN
    
    async with httpx.AsyncClient() as client:
        try:
            # Crear usuario de prueba
            try:
                response = await client.post(
                    f"{API_GATEWAY_URL}/users/", 
                    json=test_user
                )
                if response.status_code == 201:
                    logger.info("Usuario creado correctamente")
                else:
                    logger.info(f"El usuario ya existe o hubo un error: {response.status_code}")
            except Exception as e:
                logger.error(f"Error al crear usuario: {e}")
            
            # Login
            response = await client.post(
                f"{API_GATEWAY_URL}/users/login",
                data={"username": test_user["email"], "password": test_user["password"]}
            )
            
            if response.status_code == 200:
                AUTH_TOKEN = response.json()["access_token"]
                logger.info("Token obtenido correctamente")
                return AUTH_TOKEN
            else:
                logger.error(f"Error al obtener token: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Error de autenticación: {e}")
            return ""

# Imprimir respuesta
async def print_response(response):
    logger.info(f"Status: {response.status_code}")
    try:
        logger.info(f"Response: {response.json()}")
    except:
        logger.info(f"Response: {response.text}")

# 1. Crear un lugar con datos mínimos
async def test_create_place():
    logger.info("\n=== TEST: Crear lugar ===")
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONTENT_SERVICE_URL}/places/",
            json=simple_place,
            headers=headers
        )
        
        await print_response(response)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Error al crear lugar: {response.status_code}")
            return None

# 2. Crear una imagen para un lugar
async def test_create_image(place_id):
    logger.info("\n=== TEST: Crear imagen ===")
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Añadir place_id a los datos de la imagen
    image_data = simple_image.copy()
    image_data["place_id"] = place_id
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONTENT_SERVICE_URL}/images/",
            json=image_data,
            headers=headers
        )
        
        await print_response(response)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Error al crear imagen: {response.status_code}")
            return None

# 3. Crear una reseña para un lugar
async def test_create_review(place_id):
    logger.info("\n=== TEST: Crear reseña ===")
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Añadir place_id a los datos de la reseña
    review_data = simple_review.copy()
    review_data["place_id"] = place_id
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONTENT_SERVICE_URL}/reviews/",
            json=review_data,
            headers=headers
        )
        
        await print_response(response)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Error al crear reseña: {response.status_code}")
            return None

# 4. Crear un estado de sendero para un lugar
async def test_create_trail_status(place_id):
    logger.info("\n=== TEST: Crear estado de sendero ===")
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Añadir place_id a los datos del estado de sendero
    status_data = simple_trail_status.copy()
    status_data["place_id"] = place_id
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONTENT_SERVICE_URL}/trail-status/",
            json=status_data,
            headers=headers
        )
        
        await print_response(response)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Error al crear estado de sendero: {response.status_code}")
            return None

# Prueba secuencial de todos los endpoints
async def run_tests():
    # 1. Crear lugar
    place = await test_create_place()
    if not place:
        logger.error("No se pudo crear el lugar. Abortando pruebas.")
        return
    
    place_id = place["id"]
    logger.info(f"Lugar creado con ID: {place_id}")
    
    # 2. Crear imagen para el lugar
    image = await test_create_image(place_id)
    if image:
        logger.info(f"Imagen creada con ID: {image['id']}")
    
    # 3. Crear reseña para el lugar
    review = await test_create_review(place_id)
    if review:
        logger.info(f"Reseña creada con ID: {review['id']}")
    
    # 4. Crear estado de sendero para el lugar
    status = await test_create_trail_status(place_id)
    if status:
        logger.info(f"Estado de sendero creado con ID: {status['id']}")
    
    logger.info("\nPruebas completadas.")

# Ejecutar pruebas
if __name__ == "__main__":
    asyncio.run(run_tests())