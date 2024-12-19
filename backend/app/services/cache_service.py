from datetime import datetime, timedelta
import json
from typing import Any, Dict, Optional, Union
import redis
from redis.client import Redis
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        default_ttl: int = 3600  # 1 hora por defecto
    ):
        self.redis: Redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.default_ttl = default_ttl

    async def get(self, key: str) -> Optional[Dict]:
        """Obtiene un valor de la caché."""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error al obtener de caché: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Guarda un valor en la caché."""
        try:
            ttl = ttl if ttl is not None else self.default_ttl
            return self.redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Error al guardar en caché: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Elimina un valor de la caché."""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error al eliminar de caché: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """Verifica si una clave existe en la caché."""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error al verificar existencia en caché: {str(e)}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Elimina todas las claves que coinciden con un patrón."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error al limpiar patrón de caché: {str(e)}")
            return 0

    async def get_ttl(self, key: str) -> int:
        """Obtiene el tiempo de vida restante de una clave."""
        try:
            return self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Error al obtener TTL: {str(e)}")
            return -1

    async def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Extiende el tiempo de vida de una clave."""
        try:
            current_ttl = await self.get_ttl(key)
            if current_ttl > 0:
                value = await self.get(key)
                if value is not None:
                    return await self.set(key, value, current_ttl + additional_seconds)
            return False
        except Exception as e:
            logger.error(f"Error al extender TTL: {str(e)}")
            return False

def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    skip_cache_if: Optional[callable] = None
):
    """
    Decorador para cachear resultados de funciones.
    
    :param ttl: Tiempo de vida en segundos
    :param key_prefix: Prefijo para la clave de caché
    :param skip_cache_if: Función que determina si se debe saltar la caché
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Asegurarse de que tenemos acceso al servicio de caché
            if not hasattr(self, 'cache_service'):
                raise AttributeError(
                    "La clase debe tener un atributo 'cache_service' de tipo CacheService"
                )
            
            # Generar clave de caché
            cache_key = f"{key_prefix}:{func.__name__}:"
            cache_key += ":".join(str(arg) for arg in args)
            cache_key += ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            # Verificar si debemos saltar la caché
            if skip_cache_if and skip_cache_if(*args, **kwargs):
                return await func(self, *args, **kwargs)
            
            # Intentar obtener de caché
            cached_value = await self.cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit para {cache_key}")
                return cached_value
            
            # Si no está en caché, ejecutar función
            result = await func(self, *args, **kwargs)
            
            # Guardar en caché
            if result is not None:
                await self.cache_service.set(
                    cache_key,
                    result,
                    ttl
                )
            
            return result
        return wrapper
    return decorator

class AEATCache:
    """Clase específica para caché de operaciones AEAT."""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service

    async def cache_invoice_status(
        self,
        invoice_id: str,
        status: Dict,
        ttl: int = 300  # 5 minutos por defecto
    ):
        """Cachea el estado de una factura."""
        key = f"invoice_status:{invoice_id}"
        await self.cache.set(key, status, ttl)

    async def get_invoice_status(
        self,
        invoice_id: str
    ) -> Optional[Dict]:
        """Obtiene el estado cacheado de una factura."""
        key = f"invoice_status:{invoice_id}"
        return await self.cache.get(key)

    async def cache_certificate_status(
        self,
        cert_id: str,
        status: Dict,
        ttl: int = 86400  # 24 horas por defecto
    ):
        """Cachea el estado de un certificado."""
        key = f"cert_status:{cert_id}"
        await self.cache.set(key, status, ttl)

    async def get_certificate_status(
        self,
        cert_id: str
    ) -> Optional[Dict]:
        """Obtiene el estado cacheado de un certificado."""
        key = f"cert_status:{cert_id}"
        return await self.cache.get(key)

    async def invalidate_invoice_cache(self, invoice_id: str):
        """Invalida la caché de una factura."""
        key = f"invoice_status:{invoice_id}"
        await self.cache.delete(key)

    async def invalidate_certificate_cache(self, cert_id: str):
        """Invalida la caché de un certificado."""
        key = f"cert_status:{cert_id}"
        await self.cache.delete(key)

    async def cleanup_expired_invoices(self):
        """Limpia la caché de facturas expiradas."""
        return await self.cache.clear_pattern("invoice_status:*")

    async def cleanup_expired_certificates(self):
        """Limpia la caché de certificados expirados."""
        return await self.cache.clear_pattern("cert_status:*")
