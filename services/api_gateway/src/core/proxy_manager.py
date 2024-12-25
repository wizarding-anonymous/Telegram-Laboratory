# services\api_gateway\src\core\proxy_manager.py
from typing import Dict, Optional, Any, List, Union
import time
import json
from urllib.parse import urljoin
import aiohttp
from fastapi import Request, Response
from starlette.background import BackgroundTasks
from starlette.responses import StreamingResponse

from src.core.config import settings
from src.core.logger import get_logger
from src.core.exceptions import ServiceUnavailableError, ProxyError
from src.core.load_balancer import get_load_balancer
from src.core.cache_manager import get_cache_manager
from src.core.metrics import get_metrics_manager

logger = get_logger(__name__)

class ProxyManager:
    """
    Менеджер прокси для API Gateway.
    Обрабатывает и перенаправляет запросы к микросервисам.
    """

    def __init__(self) -> None:
        """Инициализация менеджера прокси."""
        self.load_balancer = get_load_balancer()
        self.cache_manager = get_cache_manager()
        self.metrics_manager = get_metrics_manager()
        
        # Настройки HTTP клиента
        self.timeout = aiohttp.ClientTimeout(
            total=settings.PROXY_TIMEOUT_SECONDS,
            connect=settings.PROXY_CONNECT_TIMEOUT_SECONDS
        )
        
        # Конфигурация ретраев
        self.max_retries = settings.PROXY_MAX_RETRIES
        self.retry_delay = settings.PROXY_RETRY_DELAY_SECONDS

    async def proxy_request(
        self,
        request: Request,
        service_name: str,
        path: str,
        background_tasks: Optional[BackgroundTasks] = None,
        **kwargs
    ) -> Response:
        """
        Проксирование запроса к микросервису.

        Args:
            request: FastAPI Request объект
            service_name: Имя целевого сервиса
            path: Путь запроса
            background_tasks: Фоновые задачи FastAPI
            **kwargs: Дополнительные параметры для запроса

        Returns:
            Response: Ответ от микросервиса

        Raises:
            ProxyError: При ошибке проксирования
            ServiceUnavailableError: Если сервис недоступен
        """
        start_time = time.time()
        method = request.method
        
        # Проверяем кэш для GET запросов
        if method == "GET":
            cached_response = await self.cache_manager.get_cached_response(request)
            if cached_response:
                self.metrics_manager.increment_cache_hit(service_name, path)
                return cached_response
            self.metrics_manager.increment_cache_miss(service_name, path)

        # Получаем инстанс сервиса через балансировщик
        service_instance = await self.load_balancer.get_service_instance(service_name)
        target_url = urljoin(service_instance.url, path)

        # Подготавливаем заголовки и параметры запроса
        headers = await self._prepare_headers(request)
        request_params = await self._prepare_request_params(request)

        try:
            # Отправляем запрос к микросервису
            response = await self._send_request(
                method,
                target_url,
                service_instance,
                headers=headers,
                **request_params,
                **kwargs
            )

            # Обрабатываем ответ
            processed_response = await self._process_response(
                request,
                response,
                service_name,
                path,
                start_time,
                background_tasks
            )

            return processed_response

        except Exception as e:
            # Обрабатываем ошибки и собираем метрики
            self._handle_proxy_error(e, service_name, path, start_time)
            raise

    async def _send_request(
        self,
        method: str,
        url: str,
        service_instance: Any,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Отправка запроса к микросервису с поддержкой ретраев.

        Args:
            method: HTTP метод
            url: URL микросервиса
            service_instance: Экземпляр сервиса
            **kwargs: Параметры запроса

        Returns:
            aiohttp.ClientResponse: Ответ от микросервиса

        Raises:
            ProxyError: При ошибке запроса
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            for attempt in range(self.max_retries):
                try:
                    service_instance.mark_request_start()
                    start_time = time.time()
                    
                    async with session.request(method, url, **kwargs) as response:
                        response_time = time.time() - start_time
                        
                        service_instance.mark_request_complete(
                            response_time,
                            failed=response.status >= 500
                        )

                        if response.status < 500:
                            return response

                except Exception as e:
                    service_instance.mark_request_complete(
                        time.time() - start_time,
                        failed=True
                    )
                    
                    if attempt == self.max_retries - 1:
                        raise ProxyError(f"Failed to proxy request: {str(e)}")

                # Ждем перед повторной попыткой
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

            raise ProxyError("Max retries exceeded")

    async def _process_response(
        self,
        request: Request,
        response: aiohttp.ClientResponse,
        service_name: str,
        path: str,
        start_time: float,
        background_tasks: Optional[BackgroundTasks]
    ) -> Response:
        """
        Обработка ответа от микросервиса.

        Args:
            request: Исходный запрос
            response: Ответ от микросервиса
            service_name: Имя сервиса
            path: Путь запроса
            start_time: Время начала запроса
            background_tasks: Фоновые задачи FastAPI

        Returns:
            Response: Обработанный ответ
        """
        # Собираем метрики
        response_time = time.time() - start_time
        self.metrics_manager.record_request_metric(
            service_name,
            path,
            request.method,
            response.status,
            response_time
        )

        # Подготавливаем заголовки ответа
        headers = self._prepare_response_headers(response)

        # Для стриминг ответов
        if response.headers.get("transfer-encoding") == "chunked":
            return StreamingResponse(
                response.content,
                status_code=response.status,
                headers=headers
            )

        # Для обычных ответов
        content = await response.read()
        fastapi_response = Response(
            content=content,
            status_code=response.status,
            headers=headers
        )

        # Кэшируем GET запросы если нужно
        if (
            request.method == "GET"
            and response.status == 200
            and background_tasks is not None
        ):
            background_tasks.add_task(
                self.cache_manager.cache_response,
                request,
                fastapi_response
            )

        return fastapi_response

    async def _prepare_headers(self, request: Request) -> Dict[str, str]:
        """Подготовка заголовков для проксируемого запроса."""
        headers = dict(request.headers)
        
        # Удаляем заголовки, которые не нужно проксировать
        headers.pop("host", None)
        headers.pop("connection", None)
        
        # Добавляем служебные заголовки
        headers["X-Forwarded-For"] = request.client.host
        headers["X-Forwarded-Proto"] = request.url.scheme
        headers["X-Forwarded-Host"] = request.headers.get("host", "")
        
        return headers

    async def _prepare_request_params(self, request: Request) -> Dict[str, Any]:
        """Подготовка параметров для проксируемого запроса."""
        params = {
            "params": request.query_params,
            "allow_redirects": False
        }

        if request.method not in ["GET", "HEAD"]:
            body = await request.body()
            if body:
                params["data"] = body

        return params

    def _prepare_response_headers(
        self,
        response: aiohttp.ClientResponse
    ) -> Dict[str, str]:
        """Подготовка заголовков для ответа клиенту."""
        headers = dict(response.headers)
        
        # Удаляем заголовки, которые не нужно передавать клиенту
        headers.pop("transfer-encoding", None)
        headers.pop("connection", None)
        
        return headers

    def _handle_proxy_error(
        self,
        error: Exception,
        service_name: str,
        path: str,
        start_time: float
    ) -> None:
        """Обработка ошибок проксирования."""
        response_time = time.time() - start_time
        
        # Записываем метрики ошибки
        self.metrics_manager.record_request_metric(
            service_name,
            path,
            "ERROR",
            500,
            response_time
        )
        
        # Логируем ошибку
        logger.error(
            f"Proxy error for {service_name} at {path}: {str(error)}",
            exc_info=error
        )


# Создание синглтона для использования в приложении
_proxy_manager: Optional[ProxyManager] = None

def get_proxy_manager() -> ProxyManager:
    """
    Получение экземпляра ProxyManager.

    Returns:
        ProxyManager instance
    """
    global _proxy_manager
    
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    
    return _proxy_manager