# services\api_gateway\src\core\service_registry.py
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.service_repository import ServiceRepository
from src.db.models.service_model import Service, ServiceStatus
from src.core.exceptions import ServiceRegistrationError, ServiceNotFoundError
from src.core.config import settings

logger = structlog.get_logger(__name__)


class ServiceRegistry:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = ServiceRepository(session)
        self._health_check_tasks: Dict[str, asyncio.Task] = {}

    async def register_service(
        self,
        name: str,
        host: str,
        port: int,
        health_check_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        weight: int = 1
    ) -> Service:
        """Register new service in registry."""
        try:
            service_data = {
                "name": name,
                "host": host,
                "port": port,
                "health_check_url": health_check_url,
                "metadata": metadata or {},
                "weight": weight,
                "status": ServiceStatus.STARTING
            }

            service = await self._repository.register(service_data)

            if health_check_url:
                self._start_health_checks(service.id)

            logger.info(f"Service registered successfully: {name}")
            return service

        except Exception as e:
            logger.error(f"Failed to register service {name}: {str(e)}")
            raise ServiceRegistrationError(f"Service registration failed: {str(e)}")

    async def deregister_service(self, service_id: str) -> None:
        """Remove service from registry."""
        try:
            if service_id in self._health_check_tasks:
                self._health_check_tasks[service_id].cancel()
                del self._health_check_tasks[service_id]

            await self._repository.delete(service_id)
            logger.info(f"Service deregistered: {service_id}")

        except Exception as e:
            logger.error(f"Failed to deregister service {service_id}: {str(e)}")
            raise

    async def get_service(self, service_id: str) -> Service:
        """Get service by ID."""
        service = await self._repository.get_by_id(service_id)
        if not service:
            raise ServiceNotFoundError(f"Service {service_id} not found")
        return service

    async def get_service_by_name(self, name: str) -> Service:
        """Get service by name."""
        service = await self._repository.get_by_name(name)
        if not service:
            raise ServiceNotFoundError(f"Service {name} not found")
        return service

    async def get_healthy_services(self) -> List[Service]:
        """Get all healthy services."""
        return await self._repository.get_healthy_services()

    async def update_service_status(
        self,
        service_id: str,
        status: ServiceStatus,
        check_time: Optional[datetime] = None
    ) -> Service:
        """Update service health status."""
        return await self._repository.update_status(service_id, status, check_time)

    async def discover_service(
        self,
        service_name: str,
        preferred_status: ServiceStatus = ServiceStatus.HEALTHY
    ) -> Service:
        """Discover available service instance."""
        services = await self._repository.get_services_by_status(preferred_status)

        if not services:
            raise ServiceNotFoundError(
                f"No {preferred_status.value} instances of {service_name} found"
            )

        # Basic round-robin selection
        return services[0]

    def _start_health_checks(self, service_id: str) -> None:
        """Start background health check task."""
        if service_id not in self._health_check_tasks:
            self._health_check_tasks[service_id] = asyncio.create_task(
                self._health_check_loop(service_id)
            )

    async def _health_check_loop(self, service_id: str) -> None:
        """Periodic health check loop for service."""
        import aiohttp

        while True:
            try:
                service = await self.get_service(service_id)

                if not service.health_check_url:
                    return

                async with aiohttp.ClientSession() as session:
                    try:
                        start_time = datetime.utcnow()
                        async with session.get(
                            f"{service.url}{service.health_check_url}",
                            timeout=settings.HEALTH_CHECK_TIMEOUT_SECONDS
                        ) as response:
                            is_healthy = response.status == 200
                            check_time = datetime.utcnow()

                            await self.update_service_status(
                                service_id,
                                ServiceStatus.HEALTHY if is_healthy else ServiceStatus.UNHEALTHY,
                                check_time
                            )

                    except Exception as e:
                        logger.warning(f"Health check failed for {service.name}: {str(e)}")
                        await self.update_service_status(
                            service_id,
                            ServiceStatus.UNHEALTHY,
                            datetime.utcnow()
                        )

                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL_SECONDS)

            except Exception as e:
                logger.error(f"Error in health check loop for {service_id}: {str(e)}")
                await asyncio.sleep(60)  # Retry delay

    async def shutdown(self) -> None:
        """Shutdown service registry."""
        for task in self._health_check_tasks.values():
            task.cancel()

        await asyncio.gather(*self._health_check_tasks.values(), return_exceptions=True)
        self._health_check_tasks.clear()
