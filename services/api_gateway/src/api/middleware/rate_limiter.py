# services\api_gateway\src\api\middleware\rate_limiter.py
from typing import Dict, Optional, Tuple
import time
from datetime import datetime
import asyncio
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.exceptions import RateLimitExceededError
from src.core.config import settings
from src.core.logger import get_logger
from src.core.redis import RedisClient

logger = get_logger(__name__)

class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware для ограничения частоты запросов к API.
    Использует Redis для хранения счетчиков запросов.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        redis_client: RedisClient,
        rate_limit: int = settings.RATE_LIMIT_PER_MINUTE,
        window_size: int = 60  # окно в секундах
    ) -> None:
        """
        Инициализация Rate Limiter.

        Args:
            app: ASGI приложение
            redis_client: Клиент Redis для хранения счетчиков
            rate_limit: Максимальное количество запросов в минуту
            window_size: Размер временного окна в секундах
        """
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = rate_limit
        self.window_size = window_size
        self._cleanup_task: Optional[asyncio.Task] = None

    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Response:
        """
        Обработка входящего запроса с проверкой лимитов.

        Args:
            request: FastAPI Request объект
            call_next: Следующий обработчик в цепочке middleware

        Returns:
            Response объект

        Raises:
            RateLimitExceededError: Если превышен лимит запросов
        """
        # Получаем идентификатор клиента
        client_id = self._get_client_identifier(request)
        
        # Проверяем и обновляем счетчик запросов
        current_count = await self._increment_request_count(client_id)
        
        # Если лимит превышен, возвращаем ошибку
        if current_count > self.rate_limit:
            reset_time = await self._get_window_reset_time(client_id)
            raise RateLimitExceededError(
                reset_time=reset_time,
                limit=self.rate_limit
            )

        # Добавляем заголовки с информацией о лимитах
        response = await call_next(request)
        remaining = max(0, self.rate_limit - current_count)
        reset_time = await self._get_window_reset_time(client_id)
        
        self._add_rate_limit_headers(
            response,
            remaining,
            reset_time,
            current_count
        )
        
        return response

    def _get_client_identifier(self, request: Request) -> str:
        """
        Получение уникального идентификатора клиента.
        По умолчанию использует IP-адрес, но может быть расширен
        для использования API ключей или других идентификаторов.

        Args:
            request: FastAPI Request объект

        Returns:
            Строка-идентификатор клиента
        """
        # Приоритет: API ключ > IP адрес
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"rate_limit:api:{api_key}"
            
        ip = request.client.host
        return f"rate_limit:ip:{ip}"

    async def _increment_request_count(self, client_id: str) -> int:
        """
        Увеличение счетчика запросов для клиента.
        Использует Redis для атомарного инкремента и установки TTL.

        Args:
            client_id: Идентификатор клиента

        Returns:
            Текущее количество запросов
        """
        async with self.redis_client.pipeline() as pipe:
            current_time = int(time.time())
            window_key = f"{client_id}:{current_time // self.window_size}"
            
            # Инкрементируем счетчик и устанавливаем TTL атомарно
            await pipe.incr(window_key)
            await pipe.expire(window_key, self.window_size * 2)
            result = await pipe.execute()
            
            return result[0]  # Возвращаем результат инкремента

    async def _get_window_reset_time(self, client_id: str) -> int:
        """
        Получение времени сброса текущего окна.

        Args:
            client_id: Идентификатор клиента

        Returns:
            Timestamp времени сброса
        """
        current_time = int(time.time())
        window_start = (current_time // self.window_size) * self.window_size
        return window_start + self.window_size

    def _add_rate_limit_headers(
        self,
        response: Response,
        remaining: int,
        reset_time: int,
        current: int
    ) -> None:
        """
        Добавление HTTP заголовков с информацией о лимитах.

        Args:
            response: Response объект
            remaining: Оставшееся количество запросов
            reset_time: Время сброса окна
            current: Текущее количество запросов
        """
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        response.headers["X-RateLimit-Current"] = str(current)

    async def cleanup_expired_windows(self) -> None:
        """
        Периодическая очистка устаревших ключей в Redis.
        Запускается как фоновая задача.
        """
        while True:
            try:
                # Получаем все ключи с паттерном rate_limit:*
                async for key in self.redis_client.scan_iter("rate_limit:*"):
                    # Проверяем TTL ключа
                    ttl = await self.redis_client.ttl(key)
                    if ttl <= 0:
                        await self.redis_client.delete(key)
                
                # Ждем перед следующей итерацией
                await asyncio.sleep(self.window_size)
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой

    async def startup(self) -> None:
        """Запуск фоновой задачи очистки при старте приложения."""
        self._cleanup_task = asyncio.create_task(self.cleanup_expired_windows())

    async def shutdown(self) -> None:
        """Остановка фоновой задачи очистки при остановке приложения."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


def setup_rate_limiter(app, redis_client: RedisClient) -> None:
    """
    Настройка Rate Limiter middleware в приложении FastAPI.

    Args:
        app: FastAPI application
        redis_client: Клиент Redis
    """
    rate_limiter = RateLimiter(app, redis_client)
    
    @app.on_event("startup")
    async def start_rate_limiter():
        await rate_limiter.startup()
    
    @app.on_event("shutdown")
    async def stop_rate_limiter():
        await rate_limiter.shutdown()