# services/api_gateway/src/api/controllers/metrics_controller.py
from typing import Dict, List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge

from src.api.schemas.response_schema import MetricsResponse, ServiceMetricsResponse
from src.db.database import get_session
from src.core.utils.helpers import handle_exceptions
from src.integrations.service_discovery import ServiceDiscoveryClient
from src.integrations.auth_service import AuthService


class MetricsController:
    """
    Контроллер для сбора и управления метриками API Gateway.
    Обеспечивает сбор и анализ метрик производительности и состояния системы.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """
        Инициализация контроллера метрик.

        Args:
            session: AsyncSession - сессия базы данных
        """
        self.session = session
        self.service_discovery = ServiceDiscoveryClient()
        self.auth_service = AuthService()

        # Определение метрик Prometheus
        self.request_count = Counter(
            'api_gateway_requests_total',
            'Total number of requests processed',
            ['method', 'path', 'status_code']
        )
        
        self.request_latency = Histogram(
            'api_gateway_request_latency_seconds',
            'Request latency in seconds',
            ['method', 'path']
        )
        
        self.active_connections = Gauge(
            'api_gateway_active_connections',
            'Number of currently active connections'
        )

        self.error_count = Counter(
            'api_gateway_errors_total',
            'Total number of errors',
            ['error_type']
        )

        self.cache_hits = Counter(
            'api_gateway_cache_hits_total',
            'Total number of cache hits'
        )

        self.cache_misses = Counter(
            'api_gateway_cache_misses_total',
            'Total number of cache misses'
        )

        logger.info("MetricsController initialized with Prometheus metrics")

    @handle_exceptions
    async def record_request(
        self, 
        method: str, 
        path: str, 
        status_code: int, 
        duration: float
    ) -> None:
        """
        Записывает метрики для отдельного HTTP запроса.

        Args:
            method: str - HTTP метод запроса
            path: str - путь запроса
            status_code: int - код ответа
            duration: float - время выполнения запроса в секундах
        """
        try:
            self.request_count.labels(
                method=method,
                path=path,
                status_code=status_code
            ).inc()

            self.request_latency.labels(
                method=method,
                path=path
            ).observe(duration)

            if status_code >= 400:
                error_type = 'client_error' if status_code < 500 else 'server_error'
                self.error_count.labels(error_type=error_type).inc()

            logger.debug(
                f"Recorded metrics for {method} {path} "
                f"(status: {status_code}, duration: {duration:.3f}s)"
            )

        except Exception as e:
            logger.error(f"Error recording metrics: {str(e)}")

    @handle_exceptions
    async def record_cache_operation(self, hit: bool) -> None:
        """
        Записывает метрики для операций кэширования.

        Args:
            hit: bool - True если произошло попадание в кэш, False если промах
        """
        try:
            if hit:
                self.cache_hits.inc()
            else:
                self.cache_misses.inc()
            
            logger.debug(f"Recorded cache {'hit' if hit else 'miss'}")

        except Exception as e:
            logger.error(f"Error recording cache metrics: {str(e)}")

    @handle_exceptions
    async def update_active_connections(self, delta: int) -> None:
        """
        Обновляет счётчик активных подключений.

        Args:
            delta: int - изменение количества подключений (+1 при подключении, -1 при отключении)
        """
        try:
            self.active_connections.inc(delta)
            current = self.active_connections._value.get()
            logger.debug(f"Active connections updated: {current}")

        except Exception as e:
            logger.error(f"Error updating active connections: {str(e)}")

    @handle_exceptions
    async def get_metrics(self, user_id: int) -> MetricsResponse:
        """
        Получает текущие метрики API Gateway.

        Args:
            user_id: int - ID пользователя, запрашивающего метрики

        Returns:
            MetricsResponse: Текущие метрики системы

        Raises:
            HTTPException: При отсутствии прав доступа
        """
        logger.debug("Collecting API Gateway metrics")

        # Проверка прав пользователя
        await self.auth_service.validate_user_permissions(user_id, "view_metrics")

        try:
            metrics = {
                "total_requests": self.request_count._value.get(),
                "active_connections": self.active_connections._value.get(),
                "total_errors": self.error_count._value.get(),
                "cache_hits": self.cache_hits._value.get(),
                "cache_misses": self.cache_misses._value.get(),
                "average_latency": await self._calculate_average_latency()
            }

            logger.info("Metrics collected successfully")
            return MetricsResponse(**metrics)

        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to collect metrics"
            )

    @handle_exceptions
    async def get_service_metrics(self, service_name: str, user_id: int) -> ServiceMetricsResponse:
        """
        Получает метрики для конкретного сервиса.

        Args:
            service_name: str - имя сервиса
            user_id: int - ID пользователя

        Returns:
            ServiceMetricsResponse: Метрики сервиса

        Raises:
            HTTPException: При отсутствии сервиса или прав доступа
        """
        logger.debug(f"Collecting metrics for service: {service_name}")

        # Проверка прав пользователя
        await self.auth_service.validate_user_permissions(user_id, "view_metrics")

        # Проверка существования сервиса
        service_exists = await self.service_discovery.check_service_exists(service_name)
        if not service_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service {service_name} not found"
            )

        try:
            metrics = {
                "service_name": service_name,
                "request_count": self.request_count.labels(
                    service=service_name
                )._value.get(),
                "error_count": self.error_count.labels(
                    service=service_name
                )._value.get(),
                "average_latency": await self._calculate_service_latency(service_name)
            }

            logger.info(f"Metrics collected for service {service_name}")
            return ServiceMetricsResponse(**metrics)

        except Exception as e:
            logger.error(f"Error collecting metrics for {service_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to collect metrics for {service_name}"
            )

    async def _calculate_average_latency(self) -> float:
        """
        Вычисляет среднее время ответа по всем запросам.

        Returns:
            float: Среднее время ответа в секундах
        """
        try:
            # Получаем данные из гистограммы латентности
            samples = list(self.request_latency._samples())
            if not samples:
                return 0.0

            total_time = sum(sample[1] for sample in samples)
            total_requests = len(samples)
            
            return total_time / total_requests if total_requests > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculating average latency: {str(e)}")
            return 0.0

    async def _calculate_service_latency(self, service_name: str) -> float:
        """
        Вычисляет среднее время ответа для конкретного сервиса.

        Args:
            service_name: str - имя сервиса

        Returns:
            float: Среднее время ответа сервиса в секундах
        """
        try:
            samples = [
                sample for sample in self.request_latency._samples()
                if service_name in sample[0][1]  # проверяем метку сервиса
            ]
            
            if not samples:
                return 0.0

            total_time = sum(sample[1] for sample in samples)
            total_requests = len(samples)
            
            return total_time / total_requests if total_requests > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculating latency for {service_name}: {str(e)}")
            return 0.0