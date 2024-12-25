# services\api_gateway\src\core\load_balancer.py
from typing import Dict, List, Optional, Set
import random
import time
from enum import Enum
import asyncio
from datetime import datetime, timedelta

from src.core.config import settings
from src.core.logger import get_logger
from src.core.exceptions import ServiceUnavailableError

logger = get_logger(__name__)

class LoadBalancingStrategy(str, Enum):
    """Доступные стратегии балансировки нагрузки."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_RANDOM = "weighted_random"
    RESPONSE_TIME = "response_time"

class ServiceInstance:
    """Класс, представляющий экземпляр микросервиса."""
    
    def __init__(
        self,
        host: str,
        port: int,
        weight: int = 1,
        health_check_url: Optional[str] = None
    ) -> None:
        self.host = host
        self.port = port
        self.weight = weight
        self.health_check_url = health_check_url
        self.active_connections = 0
        self.total_requests = 0
        self.failed_requests = 0
        self.last_response_time = 0.0
        self.last_health_check = datetime.now()
        self.is_healthy = True
        self.consecutive_failures = 0

    @property
    def url(self) -> str:
        """Полный URL экземпляра сервиса."""
        return f"http://{self.host}:{self.port}"

    @property
    def failure_rate(self) -> float:
        """Процент неудачных запросов."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100

    def mark_request_start(self) -> None:
        """Отметка начала обработки запроса."""
        self.active_connections += 1
        self.total_requests += 1

    def mark_request_complete(self, response_time: float, failed: bool = False) -> None:
        """
        Отметка завершения обработки запроса.

        Args:
            response_time: Время ответа в секундах
            failed: Флаг неудачного запроса
        """
        self.active_connections = max(0, self.active_connections - 1)
        self.last_response_time = response_time
        if failed:
            self.failed_requests += 1
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0

class LoadBalancer:
    """
    Балансировщик нагрузки для API Gateway.
    Поддерживает несколько стратегий балансировки и мониторинг состояния сервисов.
    """

    def __init__(
        self,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
        health_check_interval: int = settings.HEALTH_CHECK_INTERVAL_SECONDS
    ) -> None:
        """
        Инициализация балансировщика нагрузки.

        Args:
            strategy: Стратегия балансировки
            health_check_interval: Интервал проверки здоровья в секундах
        """
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.current_index: Dict[str, int] = {}
        self._health_check_task: Optional[asyncio.Task] = None

    async def register_service(
        self,
        service_name: str,
        host: str,
        port: int,
        weight: int = 1,
        health_check_url: Optional[str] = None
    ) -> None:
        """
        Регистрация нового экземпляра сервиса.

        Args:
            service_name: Имя сервиса
            host: Хост сервиса
            port: Порт сервиса
            weight: Вес для взвешенной балансировки
            health_check_url: URL для проверки здоровья
        """
        if service_name not in self.services:
            self.services[service_name] = []
            self.current_index[service_name] = 0

        instance = ServiceInstance(host, port, weight, health_check_url)
        self.services[service_name].append(instance)
        logger.info(f"Registered new instance for service {service_name}: {instance.url}")

    async def deregister_service(
        self,
        service_name: str,
        host: str,
        port: int
    ) -> None:
        """
        Удаление экземпляра сервиса.

        Args:
            service_name: Имя сервиса
            host: Хост сервиса
            port: Порт сервиса
        """
        if service_name in self.services:
            self.services[service_name] = [
                s for s in self.services[service_name]
                if not (s.host == host and s.port == port)
            ]
            logger.info(f"Deregistered instance {host}:{port} from service {service_name}")

    async def get_service_instance(
        self,
        service_name: str
    ) -> ServiceInstance:
        """
        Получение экземпляра сервиса согласно выбранной стратегии.

        Args:
            service_name: Имя сервиса

        Returns:
            ServiceInstance: Выбранный экземпляр сервиса

        Raises:
            ServiceUnavailableError: Если нет доступных экземпляров
        """
        instances = self.services.get(service_name, [])
        healthy_instances = [i for i in instances if i.is_healthy]

        if not healthy_instances:
            raise ServiceUnavailableError(f"No healthy instances available for {service_name}")

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            instance = await self._round_robin_select(service_name, healthy_instances)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            instance = await self._least_connections_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_RANDOM:
            instance = await self._weighted_random_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
            instance = await self._response_time_select(healthy_instances)
        else:
            instance = healthy_instances[0]

        return instance

    async def _round_robin_select(
        self,
        service_name: str,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Round Robin стратегия выбора."""
        index = self.current_index[service_name]
        instance = instances[index % len(instances)]
        self.current_index[service_name] = (index + 1) % len(instances)
        return instance

    async def _least_connections_select(
        self,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Стратегия выбора по наименьшему количеству соединений."""
        return min(instances, key=lambda x: x.active_connections)

    async def _weighted_random_select(
        self,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Стратегия взвешенного случайного выбора."""
        total_weight = sum(instance.weight for instance in instances)
        r = random.uniform(0, total_weight)
        current_weight = 0
        
        for instance in instances:
            current_weight += instance.weight
            if current_weight >= r:
                return instance
                
        return instances[-1]

    async def _response_time_select(
        self,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Стратегия выбора по времени отклика."""
        return min(instances, key=lambda x: x.last_response_time)

    async def health_check_loop(self) -> None:
        """
        Периодическая проверка здоровья всех сервисов.
        Запускается как фоновая задача.
        """
        import aiohttp
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    for service_instances in self.services.values():
                        for instance in service_instances:
                            if not instance.health_check_url:
                                continue

                            try:
                                start_time = time.time()
                                async with session.get(
                                    f"{instance.url}{instance.health_check_url}",
                                    timeout=settings.HEALTH_CHECK_TIMEOUT_SECONDS
                                ) as response:
                                    response_time = time.time() - start_time
                                    
                                    instance.is_healthy = response.status == 200
                                    instance.last_health_check = datetime.now()
                                    instance.last_response_time = response_time

                            except Exception as e:
                                logger.error(
                                    f"Health check failed for {instance.url}: {str(e)}"
                                )
                                instance.is_healthy = False
                                instance.consecutive_failures += 1

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Error in health check loop: {str(e)}")
                await asyncio.sleep(60)

    async def get_service_stats(
        self,
        service_name: Optional[str] = None
    ) -> Dict:
        """
        Получение статистики по сервисам.

        Args:
            service_name: Опциональное имя сервиса

        Returns:
            Dict: Статистика по сервисам
        """
        stats = {}
        
        if service_name:
            instances = self.services.get(service_name, [])
            stats[service_name] = self._get_service_instances_stats(instances)
        else:
            for svc_name, instances in self.services.items():
                stats[svc_name] = self._get_service_instances_stats(instances)

        return stats

    def _get_service_instances_stats(
        self,
        instances: List[ServiceInstance]
    ) -> Dict:
        """Получение статистики по экземплярам сервиса."""
        total_instances = len(instances)
        healthy_instances = len([i for i in instances if i.is_healthy])
        
        return {
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "total_requests": sum(i.total_requests for i in instances),
            "active_connections": sum(i.active_connections for i in instances),
            "failed_requests": sum(i.failed_requests for i in instances),
            "instances": [
                {
                    "url": instance.url,
                    "healthy": instance.is_healthy,
                    "active_connections": instance.active_connections,
                    "total_requests": instance.total_requests,
                    "failed_requests": instance.failed_requests,
                    "failure_rate": instance.failure_rate,
                    "last_response_time": instance.last_response_time,
                    "last_health_check": instance.last_health_check.isoformat()
                }
                for instance in instances
            ]
        }

    async def startup(self) -> None:
        """Запуск балансировщика нагрузки."""
        self._health_check_task = asyncio.create_task(self.health_check_loop())
        logger.info(
            f"Load balancer started with strategy: {self.strategy.value}"
        )

    async def shutdown(self) -> None:
        """Остановка балансировщика нагрузки."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Load balancer stopped")


# Создание синглтона для использования в приложении
_load_balancer: Optional[LoadBalancer] = None

def get_load_balancer(
    strategy: Optional[LoadBalancingStrategy] = None
) -> LoadBalancer:
    """
    Получение экземпляра LoadBalancer.
    
    Args:
        strategy: Опциональная стратегия балансировки

    Returns:
        LoadBalancer instance
    """
    global _load_balancer
    
    if _load_balancer is None:
        _load_balancer = LoadBalancer(
            strategy or LoadBalancingStrategy.ROUND_ROBIN
        )
    elif strategy and _load_balancer.strategy != strategy:
        _load_balancer.strategy = strategy
    
    return _load_balancer