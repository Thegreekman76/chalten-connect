# backend\services\content-service\app\services\storage.py
from typing import Optional, Dict, Any, BinaryIO
import os
from abc import ABC, abstractmethod

class StorageService(ABC):
    """Interfaz abstracta para servicios de almacenamiento."""
    
    @abstractmethod
    async def upload_file(self, file: BinaryIO, filename: str, content_type: str) -> str:
        """
        Sube un archivo al almacenamiento y devuelve su URL pública.
        
        Args:
            file: El archivo a subir
            filename: Nombre del archivo
            content_type: Tipo MIME del archivo
            
        Returns:
            URL pública del archivo
        """
        pass
    
    @abstractmethod
    async def delete_file(self, url: str) -> bool:
        """
        Elimina un archivo del almacenamiento.
        
        Args:
            url: URL del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass

class URLStorageService(StorageService):
    """
    Implementación simple que solo almacena URLs.
    No sube realmente archivos, solo devuelve la URL que se le pasa.
    """
    
    async def upload_file(self, file: BinaryIO, filename: str, content_type: str) -> str:
        # En una implementación real, aquí se subiría el archivo
        # Por ahora, simplemente devolvemos una URL de ejemplo
        return f"https://example.com/images/{filename}"
    
    async def delete_file(self, url: str) -> bool:
        # En una implementación real, aquí se eliminaría el archivo
        # Por ahora, simplemente devolvemos True
        return True

# Factory para obtener la instancia del servicio de almacenamiento
def get_storage_service() -> StorageService:
    """
    Devuelve la implementación configurada del servicio de almacenamiento.
    En el futuro, esto podría devolver diferentes implementaciones según la configuración.
    """
    # Por ahora, siempre devolvemos URLStorageService
    return URLStorageService()