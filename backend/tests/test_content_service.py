# test_content_service_complete.py
import httpx
import asyncio
import json
import random
import string
from typing import Dict, Any, List, Optional
import logging
import sys
from datetime import datetime, timedelta

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("content-service-test")

# URLs de los servicios
API_GATEWAY_URL = "http://localhost:8000/api/v1"  # Para probar a través del API Gateway
CONTENT_SERVICE_URL = "http://localhost:8002"     # Para probar directamente el servicio

# Token de autenticación
AUTH_TOKEN = None

def generate_random_string(length=6):
    """Genera una cadena aleatoria para evitar colisiones de nombres."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Datos de prueba con valores aleatorios para evitar colisiones
test_user = {
    "email": f"test{generate_random_string()}@chalten.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
}

test_category = {
    "name": f"Senderos {generate_random_string()}",
    "description": "Rutas de senderismo en El Chaltén",
    "icon": "hiking",
    "is_active": True
}

test_place = {
    "name": f"Laguna de los Tres {generate_random_string()}",
    "description": "Hermosa laguna con vistas al Monte Fitz Roy",
    "short_description": "Vista panorámica del Fitz Roy",
    "place_type": "trail",
    "latitude": -49.2726,
    "longitude": -72.9723,
    "is_active": True,
    "is_featured": True,
    "difficulty_level": "moderate",
    "duration_minutes": 480,
    "distance_km": 20.0,
    "elevation_gain_m": 750
}

test_image = {
    "url": "https://example.com/image.jpg",
    "alt_text": "Vista de la Laguna de los Tres",
    "caption": "Laguna de los Tres con el Fitz Roy de fondo",
    "is_main": True
}

test_review = {
    "rating": 4.5,
    "title": "Excelente experiencia",
    "comment": "Uno de los mejores senderos que he recorrido"
}

test_trail_status = {
    "status": "open",
    "details": "Sendero abierto. Buenas condiciones.",
    "valid_until": (datetime.now() + timedelta(days=7)).isoformat()
}

# Funciones auxiliares
async def get_auth_token() -> str:
    """Obtiene un token de autenticación mediante login."""
    global AUTH_TOKEN
    if AUTH_TOKEN:
        return AUTH_TOKEN
    
    async with httpx.AsyncClient() as client:
        try:
            # Primero intentamos crear un usuario de prueba
            try:
                response = await client.post(
                    f"{API_GATEWAY_URL}/users/", 
                    json=test_user
                )
                if response.status_code == 201:
                    logger.info("Usuario de prueba creado correctamente")
                else:
                    logger.info(f"El usuario ya existe o hubo un error: {response.status_code}")
            except Exception as e:
                logger.error(f"Error al crear usuario: {e}")
            
            # Ahora hacemos login
            response = await client.post(
                f"{API_GATEWAY_URL}/users/login",
                data={"username": test_user["email"], "password": test_user["password"]}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                AUTH_TOKEN = token_data["access_token"]
                logger.info("Token de autenticación obtenido correctamente")
                return AUTH_TOKEN
            else:
                logger.error(f"Error al obtener token: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Error en la autenticación: {e}")
            return ""

async def print_response(response: httpx.Response) -> None:
    """Imprime detalles de la respuesta para debugging."""
    logger.info(f"Status: {response.status_code}")
    try:
        logger.info(f"Response: {response.json()}")
    except json.JSONDecodeError:
        logger.info(f"Response: {response.text}")

async def safe_request(method, url, **kwargs):
    """Realiza una solicitud HTTP de forma segura, manejando errores de conexión."""
    try:
        async with httpx.AsyncClient() as client:
            if method.lower() == "get":
                response = await client.get(url, **kwargs)
            elif method.lower() == "post":
                response = await client.post(url, **kwargs)
            elif method.lower() == "put":
                response = await client.put(url, **kwargs)
            elif method.lower() == "delete":
                response = await client.delete(url, **kwargs)
            else:
                logger.error(f"Método HTTP no soportado: {method}")
                return None
            
            return response
    except httpx.RemoteProtocolError as e:
        logger.error(f"Error de protocolo: {e}")
        return None
    except Exception as e:
        logger.error(f"Error en la solicitud {method} {url}: {e}")
        return None

# Pruebas de salud
async def test_health():
    """Prueba el endpoint de salud para verificar si el servicio está funcionando."""
    logger.info("\n=== PROBANDO ENDPOINT DE SALUD ===")
    
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/health")
    if response:
        await print_response(response)
        return response.status_code == 200
    else:
        return False

# Pruebas completas para categorías
async def test_categories_endpoints():
    """Prueba todos los endpoints relacionados con categorías."""
    logger.info("\n=== PROBANDO ENDPOINTS DE CATEGORÍAS ===")
    created_category = None
    
    # Obtener token
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token. Prueba fallida.")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Listar categorías (GET /categories/)
    logger.info("\n--- Listando todas las categorías ---")
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/categories/")
    
    if not response:
        logger.error("Error al listar categorías")
        return None
    
    await print_response(response)
    
    # 2. Crear una categoría (POST /categories/)
    logger.info("\n--- Creando una nueva categoría ---")
    response = await safe_request(
        "post", 
        f"{CONTENT_SERVICE_URL}/categories/", 
        json=test_category,
        headers=headers
    )
    
    if not response or response.status_code != 201:
        logger.error(f"Error al crear categoría: {response.status_code if response else 'Sin respuesta'}")
        return None
    
    await print_response(response)
    created_category = response.json()
    
    # 3. Obtener categoría por ID (GET /categories/{id})
    if created_category:
        category_id = created_category["id"]
        logger.info(f"\n--- Obteniendo categoría con ID {category_id} ---")
        response = await safe_request("get", f"{CONTENT_SERVICE_URL}/categories/{category_id}")
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al obtener categoría con ID {category_id}")
    
    # 4. Actualizar categoría (PUT /categories/{id})
    if created_category:
        category_id = created_category["id"]
        logger.info(f"\n--- Actualizando categoría con ID {category_id} ---")
        update_data = {"description": f"Descripción actualizada {generate_random_string()}"}
        response = await safe_request(
            "put", 
            f"{CONTENT_SERVICE_URL}/categories/{category_id}", 
            json=update_data,
            headers=headers
        )
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al actualizar categoría con ID {category_id}")
    
    # 5. Eliminar categoría (DELETE /categories/{id}) - Comentado para mantener datos para otras pruebas
    """
    if created_category:
        category_id = created_category["id"]
        logger.info(f"\n--- Eliminando categoría con ID {category_id} ---")
        response = await safe_request(
            "delete", 
            f"{CONTENT_SERVICE_URL}/categories/{category_id}", 
            headers=headers
        )
        
        if response:
            logger.info(f"Status: {response.status_code}")
        else:
            logger.error(f"Error al eliminar categoría con ID {category_id}")
    """
    
    return created_category

# Pruebas completas para lugares
async def test_places_endpoints(category = None):
    """Prueba todos los endpoints relacionados con lugares."""
    logger.info("\n=== PROBANDO ENDPOINTS DE LUGARES ===")
    created_place = None
    
    # Obtener token
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token. Prueba fallida.")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Preparar datos para el lugar
    place_data = test_place.copy()
    if category:
        place_data["category_ids"] = [category["id"]]
    
    # 1. Listar lugares (GET /places/)
    logger.info("\n--- Listando todos los lugares ---")
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/places/")
    
    if response:
        await print_response(response)
    else:
        logger.error("Error al listar lugares")
    
    # 2. Crear un lugar (POST /places/)
    logger.info("\n--- Creando un nuevo lugar ---")
    response = await safe_request(
        "post", 
        f"{CONTENT_SERVICE_URL}/places/", 
        json=place_data,
        headers=headers
    )
    
    if not response or response.status_code not in [200, 201]:
        logger.error(f"Error al crear lugar: {response.status_code if response else 'Sin respuesta'}")
        return None
    
    await print_response(response)
    created_place = response.json()
    
    # 3. Obtener lugar por ID (GET /places/{id})
    if created_place:
        place_id = created_place["id"]
        logger.info(f"\n--- Obteniendo lugar con ID {place_id} ---")
        response = await safe_request("get", f"{CONTENT_SERVICE_URL}/places/{place_id}")
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al obtener lugar con ID {place_id}")
    
    # 4. Obtener lugar por slug (GET /places/slug/{slug})
    if created_place:
        place_slug = created_place["slug"]
        logger.info(f"\n--- Obteniendo lugar con slug {place_slug} ---")
        response = await safe_request("get", f"{CONTENT_SERVICE_URL}/places/slug/{place_slug}")
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al obtener lugar con slug {place_slug}")
    
    # 5. Actualizar lugar (PUT /places/{id})
    if created_place:
        place_id = created_place["id"]
        logger.info(f"\n--- Actualizando lugar con ID {place_id} ---")
        update_data = {"short_description": f"Descripción corta actualizada {generate_random_string()}"}
        response = await safe_request(
            "put", 
            f"{CONTENT_SERVICE_URL}/places/{place_id}", 
            json=update_data,
            headers=headers
        )
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al actualizar lugar con ID {place_id}")
    
    # 6. Eliminar lugar (DELETE /places/{id}) - Comentado para mantener datos para otras pruebas
    """
    if created_place:
        place_id = created_place["id"]
        logger.info(f"\n--- Eliminando lugar con ID {place_id} ---")
        response = await safe_request(
            "delete", 
            f"{CONTENT_SERVICE_URL}/places/{place_id}", 
            headers=headers
        )
        
        if response:
            logger.info(f"Status: {response.status_code}")
        else:
            logger.error(f"Error al eliminar lugar con ID {place_id}")
    """
    
    return created_place

# Pruebas completas para imágenes
async def test_images_endpoints(place = None):
    """Prueba todos los endpoints relacionados con imágenes."""
    logger.info("\n=== PROBANDO ENDPOINTS DE IMÁGENES ===")
    created_image = None
    
    if not place:
        logger.error("No se puede probar imágenes sin un lugar asociado")
        return None
    
    # Obtener token
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token. Prueba fallida.")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Preparar datos para la imagen
    image_data = test_image.copy()
    image_data["place_id"] = place["id"]
    
    # 1. Listar imágenes (GET /images/)
    logger.info("\n--- Listando todas las imágenes ---")
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/images/")
    
    if response:
        await print_response(response)
    else:
        logger.error("Error al listar imágenes")
    
    # 2. Listar imágenes por lugar (GET /images/?place_id={place_id})
    place_id = place["id"]
    logger.info(f"\n--- Listando imágenes del lugar con ID {place_id} ---")
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/images/?place_id={place_id}")
    
    if response:
        await print_response(response)
    else:
        logger.error(f"Error al listar imágenes del lugar con ID {place_id}")
    
    # 3. Crear una imagen (POST /images/)
    logger.info("\n--- Creando una nueva imagen ---")
    response = await safe_request(
        "post", 
        f"{CONTENT_SERVICE_URL}/images/", 
        json=image_data,
        headers=headers
    )
    
    if not response or response.status_code not in [200, 201]:
        logger.error(f"Error al crear imagen: {response.status_code if response else 'Sin respuesta'}")
        return None
    
    await print_response(response)
    created_image = response.json()
    
    # 4. Obtener imagen por ID (GET /images/{id})
    if created_image:
        image_id = created_image["id"]
        logger.info(f"\n--- Obteniendo imagen con ID {image_id} ---")
        response = await safe_request("get", f"{CONTENT_SERVICE_URL}/images/{image_id}")
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al obtener imagen con ID {image_id}")
    
    # 5. Actualizar imagen (PUT /images/{id})
    if created_image:
        image_id = created_image["id"]
        logger.info(f"\n--- Actualizando imagen con ID {image_id} ---")
        update_data = {"alt_text": f"Texto alternativo actualizado {generate_random_string()}"}
        response = await safe_request(
            "put", 
            f"{CONTENT_SERVICE_URL}/images/{image_id}", 
            json=update_data,
            headers=headers
        )
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al actualizar imagen con ID {image_id}")
    
    # 6. Probar reordenenamiento de imágenes (PUT /images/reorder)
    if created_image:
        logger.info(f"\n--- Reordenando imágenes del lugar con ID {place_id} ---")
        reorder_data = {
            "image_ids": [created_image["id"]]  # Aquí solo tenemos una imagen, pero en un caso real habría varias
        }
        response = await safe_request(
            "put", 
            f"{CONTENT_SERVICE_URL}/images/reorder?place_id={place_id}", 
            json=reorder_data,
            headers=headers
        )
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al reordenar imágenes del lugar con ID {place_id}")
    
    # 7. Eliminar imagen (DELETE /images/{id}) - Comentado para mantener datos consistentes
    """
    if created_image:
        image_id = created_image["id"]
        logger.info(f"\n--- Eliminando imagen con ID {image_id} ---")
        response = await safe_request(
            "delete", 
            f"{CONTENT_SERVICE_URL}/images/{image_id}", 
            headers=headers
        )
        
        if response:
            logger.info(f"Status: {response.status_code}")
        else:
            logger.error(f"Error al eliminar imagen con ID {image_id}")
    """
    
    return created_image

# Pruebas completas para reseñas
async def test_reviews_endpoints(place = None):
    """Prueba todos los endpoints relacionados con reseñas."""
    logger.info("\n=== PROBANDO ENDPOINTS DE RESEÑAS ===")
    created_review = None
    
    if not place:
        logger.error("No se puede probar reseñas sin un lugar asociado")
        return None
    
    # Obtener token
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token. Prueba fallida.")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Preparar datos para la reseña
    review_data = test_review.copy()
    review_data["place_id"] = place["id"]
    
    # 1. Listar reseñas por lugar (GET /reviews/place/{place_id})
    place_id = place["id"]
    logger.info(f"\n--- Listando reseñas del lugar con ID {place_id} ---")
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/reviews/place/{place_id}")
    
    if response:
        await print_response(response)
    else:
        logger.error(f"Error al listar reseñas del lugar con ID {place_id}")
    
    # 2. Crear una reseña (POST /reviews/)
    logger.info("\n--- Creando una nueva reseña ---")
    response = await safe_request(
        "post", 
        f"{CONTENT_SERVICE_URL}/reviews/", 
        json=review_data,
        headers=headers
    )
    
    if not response or response.status_code not in [200, 201]:
        logger.error(f"Error al crear reseña: {response.status_code if response else 'Sin respuesta'}")
        return None
    
    await print_response(response)
    created_review = response.json()
    
    # 3. Obtener reseñas del usuario actual (GET /reviews/user/me)
    logger.info("\n--- Obteniendo reseñas del usuario actual ---")
    response = await safe_request(
        "get", 
        f"{CONTENT_SERVICE_URL}/reviews/user/me", 
        headers=headers
    )
    
    if response:
        await print_response(response)
    else:
        logger.error("Error al obtener reseñas del usuario actual")
    
    # 4. Obtener reseña por ID (GET /reviews/{id})
    if created_review:
        review_id = created_review["id"]
        logger.info(f"\n--- Obteniendo reseña con ID {review_id} ---")
        response = await safe_request("get", f"{CONTENT_SERVICE_URL}/reviews/{review_id}")
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al obtener reseña con ID {review_id}")
    
    # 5. Actualizar reseña (PUT /reviews/{id})
    if created_review:
        review_id = created_review["id"]
        logger.info(f"\n--- Actualizando reseña con ID {review_id} ---")
        update_data = {
            "rating": 5.0,
            "comment": f"Comentario actualizado {generate_random_string()}"
        }
        response = await safe_request(
            "put", 
            f"{CONTENT_SERVICE_URL}/reviews/{review_id}", 
            json=update_data,
            headers=headers
        )
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al actualizar reseña con ID {review_id}")
    
    # 6. Eliminar reseña (DELETE /reviews/{id}) - Comentado para mantener datos consistentes
    """
    if created_review:
        review_id = created_review["id"]
        logger.info(f"\n--- Eliminando reseña con ID {review_id} ---")
        response = await safe_request(
            "delete", 
            f"{CONTENT_SERVICE_URL}/reviews/{review_id}", 
            headers=headers
        )
        
        if response:
            logger.info(f"Status: {response.status_code}")
        else:
            logger.error(f"Error al eliminar reseña con ID {review_id}")
    """
    
    return created_review

# Pruebas completas para estado de senderos
async def test_trail_status_endpoints(place = None):
    """Prueba todos los endpoints relacionados con estado de senderos."""
    logger.info("\n=== PROBANDO ENDPOINTS DE ESTADO DE SENDEROS ===")
    created_status = None
    
    if not place:
        logger.error("No se puede probar estado de senderos sin un lugar asociado")
        return None
    
    # Obtener token
    token = await get_auth_token()
    if not token:
        logger.error("No se pudo obtener token. Prueba fallida.")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Preparar datos para el estado de sendero
    status_data = test_trail_status.copy()
    status_data["place_id"] = place["id"]
    
    # 1. Crear un estado de sendero (POST /trail-status/)
    logger.info("\n--- Creando un nuevo estado de sendero ---")
    response = await safe_request(
        "post", 
        f"{CONTENT_SERVICE_URL}/trail-status/", 
        json=status_data,
        headers=headers
    )
    
    if not response or response.status_code not in [200, 201]:
        logger.error(f"Error al crear estado de sendero: {response.status_code if response else 'Sin respuesta'}")
        return None
    
    await print_response(response)
    created_status = response.json()
    
    # 2. Obtener estado actual del sendero (GET /trail-status/place/{place_id}/current)
    place_id = place["id"]
    logger.info(f"\n--- Obteniendo estado actual del sendero con ID {place_id} ---")
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/trail-status/place/{place_id}/current")
    
    if response:
        await print_response(response)
    else:
        logger.error(f"Error al obtener estado actual del sendero con ID {place_id}")
    
    # 3. Obtener historial de estados del sendero (GET /trail-status/place/{place_id}/history)
    logger.info(f"\n--- Obteniendo historial de estados del sendero con ID {place_id} ---")
    response = await safe_request("get", f"{CONTENT_SERVICE_URL}/trail-status/place/{place_id}/history")
    
    if response:
        await print_response(response)
    else:
        logger.error(f"Error al obtener historial de estados del sendero con ID {place_id}")
    
    # 4. Actualizar estado de sendero (PUT /trail-status/{id})
    if created_status:
        status_id = created_status["id"]
        logger.info(f"\n--- Actualizando estado de sendero con ID {status_id} ---")
        update_data = {
            "status": "partially_open",
            "details": f"Actualización: Algunas zonas con precauciones por lluvia reciente {generate_random_string()}"
        }
        response = await safe_request(
            "put", 
            f"{CONTENT_SERVICE_URL}/trail-status/{status_id}", 
            json=update_data,
            headers=headers
        )
        
        if response:
            await print_response(response)
        else:
            logger.error(f"Error al actualizar estado de sendero con ID {status_id}")
    
    return created_status

# Función principal para ejecutar todas las pruebas
async def run_all_tests():
    """Ejecuta pruebas completas de todos los endpoints del servicio de contenido."""
    logger.info("Iniciando pruebas completas del servicio de contenido...\n")
    
    # Probar endpoint de salud
    if not await test_health():
        logger.error("El servicio no está respondiendo correctamente. Abortando pruebas.")
        return
    
    # Probar endpoints de categorías
    category = await test_categories_endpoints()
    
    # Probar endpoints de lugares
    place = await test_places_endpoints(category)
    
    if place:
        # Probar endpoints de imágenes
        image = await test_images_endpoints(place)
        
        # Probar endpoints de reseñas
        review = await test_reviews_endpoints(place)
        
        # Probar endpoints de estado de senderos
        trail_status = await test_trail_status_endpoints(place)
    
    logger.info("\nPruebas completas finalizadas.")

# Ejecutar pruebas si el script se ejecuta directamente
if __name__ == "__main__":
    asyncio.run(run_all_tests())