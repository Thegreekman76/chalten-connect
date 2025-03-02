# backend\services\content-service\app\utils\slug.py
import re
import unicodedata

def create_slug(text):
    """
    Crea un slug a partir de un texto.
    Convierte texto a minúsculas, elimina caracteres especiales,
    reemplaza espacios con guiones y convierte caracteres acentuados.
    
    Args:
        text: Texto para convertir a slug
        
    Returns:
        Texto convertido a slug
    """
    # Convertir a minúsculas
    text = str(text).lower().strip()
    
    # Normalizar caracteres Unicode (convertir acentos, etc.)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Reemplazar caracteres no alfanuméricos con guiones
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Eliminar guiones al principio o final
    text = text.strip('-')
    
    # Eliminar guiones duplicados
    text = re.sub(r'-+', '-', text)
    
    return text