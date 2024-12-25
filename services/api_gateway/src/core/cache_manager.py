# services\api_gateway\src\core\cache_manager.py
from typing import Any, Dict, Optional, Union
import json
import hashlib
from datetime import datetime, timedelta

from fastapi import Request, Response
from starlette.responses import JSONResponse

from src.core.config import settings
from src.core.redis import RedisClient
from src.core.logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    """
    Менеджер кэширования для API Gateway.
    Управляет кэшированием ответов от микросервисов используя Redis.
    """

    def __init__(self, redis_client: RedisClient) -> None:
        """
        Инициализация менеджера кэширования.

        Args:
            redis_client: Клиент Redis для хранения кэша
        """
        self.redis = redis_client
        self.default_ttl = settings.CACHE_TTL_SECONDS
        self.enabled = settings.CACHE_ENABLED

    async def get_cached_response(
        self,
        request: Request,
        cache_key: Optional[str] = None
    ) -> Optional[Response]:
        """
        Получение закэшированного ответа для запроса.

        Args:
            request: FastAPI Request объект
            cache_key: Опциональный ключ кэша

        Returns:
            Response объект если кэш найден, иначе None
        """
        if not self.enabled:
            return None

        key = cache_key or await self._generate_cache_key(request)
        cached_data = await self.redis.get(key)

        if not cached_data:
            return None

        try:
            cached_response = json.loads(cached_data)
            return JSONResponse(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response.get("headers", {})
            )
        except Exception as e:
            logger.error(f"Error deserializing cached response: {e}")
            await self.redis.delete(key)
            return None

    async def cache_response(
        self,
        request: Request,
        response: Response,
        ttl: Optional[int] = None,
        cache_key: Optional[str] = None
    ) -> None:
        """
        Кэширование ответа на запрос.

        Args:
            request: FastAPI Request объект
            response: Response объект для кэширования
            ttl: Время жизни кэша в секундах
            cache_key: Опциональный ключ кэша
        """
        if not self.enabled or not self._should_cache_response(response):
            return

        key = cache_key or await self._generate_cache_key(request)
        ttl = ttl or self.default_ttl

        try:
            # Получаем контент из response
            if isinstance(response, JSONResponse):
                content = response.body.decode()
                content = json.loads(content)
            else:
                content = await self._get_response_content(response)

            # Создаем объект для кэширования
            cache_data = {
                "content": content,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "cached_at": datetime.utcnow().isoformat()
            }

            # Сохраняем в Redis
            await self.redis.setex(
                key,
                ttl,
                json.dumps(cache_data)
            )

        except Exception as e:
            logger.error(f"Error caching response: {e}")

    async def invalidate_cache(
        self,
        pattern: str = "*"
    ) -> int:
        """
        Инвалидация кэша по паттерну.

        Args:
            pattern: Паттерн для поиска ключей

        Returns:
            Количество удаленных ключей
        """
        deleted_count = 0
        try:
            async for key in self.redis.scan_iter(f"cache:{pattern}"):
                await self.redis.delete(key)
                deleted_count += 1
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
        
        return deleted_count

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получение статистики кэширования.

        Returns:
            Словарь со статистикой
        """
        try:
            total_keys = 0
            total_memory = 0
            
            async for key in self.redis.scan_iter("cache:*"):
                total_keys += 1
                memory = await self.redis.memory_usage(key)
                total_memory += memory or 0

            return {
                "total_cached_items": total_keys,
                "total_memory_bytes": total_memory,
                "cache_enabled": self.enabled,
                "default_ttl": self.default_ttl
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "error": str(e),
                "cache_enabled": self.enabled,
                "default_ttl": self.default_ttl
            }

    async def _generate_cache_key(self, request: Request) -> str:
        """
        Генерация ключа кэша на основе параметров запроса.

        Args:
            request: FastAPI Request объект

        Returns:
            Строка ключа кэша
        """
        # Получаем основные компоненты запроса
        method = request.method
        path = request.url.path
        query_params = str(sorted(request.query_params.items()))
        headers = self._get_cache_headers(request)
        
        # Создаем уникальный ключ
        key_components = [method, path, query_params, headers]
        
        # Если есть тело запроса, добавляем его в компоненты
        body = await self._get_request_body(request)
        if body:
            key_components.append(body)
            
        # Генерируем хэш
        key_string = "|".join(key_components)
        hash_object = hashlib.sha256(key_string.encode())
        hash_value = hash_object.hexdigest()
        
        return f"cache:{hash_value}"

    def _get_cache_headers(self, request: Request) -> str:
        """
        Получение заголовков, влияющих на кэширование.

        Args:
            request: FastAPI Request объект

        Returns:
            Строка с заголовками
        """
        cache_headers = [
            "accept",
            "accept-encoding",
            "accept-language",
            "x-api-version"
        ]
        
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() in cache_headers
        }
        
        return str(sorted(headers.items()))

    async def _get_request_body(self, request: Request) -> str:
        """
        Получение тела запроса.

        Args:
            request: FastAPI Request объект

        Returns:
            Строка с телом запроса
        """
        try:
            body = await request.body()
            return body.decode()
        except Exception:
            return ""

    async def _get_response_content(self, response: Response) -> Any:
        """
        Получение контента из response.

        Args:
            response: Response объект

        Returns:
            Контент ответа
        """
        if hasattr(response, "body"):
            return json.loads(response.body.decode())
        return None

    def _should_cache_response(self, response: Response) -> bool:
        """
        Проверка, нужно ли кэшировать ответ.

        Args:
            response: Response объект

        Returns:
            bool: True если ответ можно кэшировать
        """
        # Кэшируем только успешные ответы
        if response.status_code not in {200, 201, 203, 204, 206, 300, 301, 302, 304}:
            return False

        # Проверяем заголовки кэширования
        cache_control = response.headers.get("cache-control", "").lower()
        if "no-store" in cache_control or "no-cache" in cache_control:
            return False

        return True


# Создание синглтона для использования в приложении
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(redis_client: Optional[RedisClient] = None) -> CacheManager:
    """
    Получение экземпляра CacheManager.
    
    Args:
        redis_client: Опциональный клиент Redis

    Returns:
        CacheManager instance
    """
    global _cache_manager
    
    if _cache_manager is None:
        if redis_client is None:
            raise ValueError("Redis client is required for initial setup")
        _cache_manager = CacheManager(redis_client)
    
    return _cache_manager