# El Chaltén Connect - Backend

Plataforma integral para turismo en El Chaltén que conecta visitantes con servicios locales mientras
ofrece funcionalidades especializadas para áreas remotas de montaña.

# Listar archivos y carpetas

find . -type f -not -path "_/\._" -not -path "_/alembic/_" -not -path "_/**pycache**/_" | sort

---

# Usuarios de prueba

## Admin

### name: tourist@example.com

### pass: password123

## TOURIST

### name: tourist@example.com

### pass: password123

---

# APIs

## API Gateway

### http://localhost:8000/api/v1/docs

## API User Service

### http://localhost:8001/docs

---

# Docker

## Ejecutar

### Desde backend/docker

### **Comandos Útiles**

| Descripción                          | Comando                                                                                                                                       |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Detener Docker                       | `docker-compose down -v`                                                                                                                      |
| Ver logs de PostgreSQL               | `docker logs molecule_db`                                                                                                                     |
| Reiniciar el servicio                | `docker-compose restart backend`                                                                                                              |
| Verificar el estado de los servicios | `docker-compose ps`                                                                                                                           |
| Reconstruir servicios                | `docker-compose up --build -d `                                                                                                               |
| Entrar al backend para debugear      | `docker exec -it molecule_backend bash`                                                                                                       |
| Monitorear logs en tiempo real       | `docker-compose logs -f backend `                                                                                                             |
| Entrar a la consola de PostgreSQL    | `docker exec -it molecule_db psql -U admin molecule_db`                                                                                       |
| Ejecutar                             | `docker-compose up -d`                                                                                                                        |
| Ver logs del Backen                  | `docker-compose logs backend`                                                                                                                 |
| Probar endpoints                     | `docker exec molecule_backend curl -s http://localhost:8000 `                                                                                 |
| Verificar coneccion postgres         | `docker exec -it molecule_backend bash -c "psql -U admin -h postgres -d molecule_db -c '\dt'"molecule_backend curl -s http://localhost:8000 ` |

### Limpiar todo completamente

docker system prune -af
docker volume prune -f
docker-compose down -v --remove-orphans

### Reconstruir con caché fresca

docker-compose up --force-recreate --build -d

---

# Futuras implementaciones

## content-service

### imagenes service

#### En tus routes o controladores

Cambiar entre implementaciones simplemente modificando la función `get_storage_service()`.

Para utilizarlo en tu código, inyectarías esta dependencia donde sea necesario:

```python
# En tus routes o controladores
from app.services.storage import get_storage_service

@router.post("/images/")
async def create_image(
    file: UploadFile,
    place_id: int,
    current_user_id: int = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Crea una nueva imagen."""
    # Subir el archivo
    url = await storage_service.upload_file(
        file.file,
        file.filename,
        file.content_type
    )

    # Crear la entrada en la base de datos con la URL
    db_image = ImageModel(
        place_id=place_id,
        url=url,
        # otros campos...
    )

    # Resto del código....
```
