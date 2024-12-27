# services\api_gateway\src\db\repositories\service_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models.service_model import Service, ServiceStatus
from src.core.exceptions import NotFoundException, ServiceRegistrationError

class ServiceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def register(self, service_data: Dict[str, Any]) -> Service:
        """Register new service."""
        try:
            service = Service(**service_data)
            self._session.add(service)
            await self._session.flush()
            return service
        except Exception as e:
            raise ServiceRegistrationError(f"Failed to register service: {str(e)}")

    async def get_by_id(self, service_id: str) -> Optional[Service]:
        """Get service by ID."""
        query = select(Service).where(Service.id == service_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Service]:
        """Get service by name."""
        query = select(Service).where(Service.name == name)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_healthy_services(self) -> List[Service]:
        """Get all healthy services."""
        query = select(Service).where(
            and_(
                Service.status == ServiceStatus.HEALTHY,
                Service.is_active is True
            )
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self,
        include_inactive: bool = False,
        statuses: Optional[List[ServiceStatus]] = None
    ) -> List[Service]:
        """Get all services with optional filters."""
        query = select(Service)

        if not include_inactive:
            query = query.where(Service.is_active is True)

        if statuses:
            query = query.where(Service.status.in_(statuses))

        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update_status(
        self,
        service_id: str,
        status: ServiceStatus,
        check_time: Optional[datetime] = None
    ) -> Service:
        """Update service health status."""
        service = await self.get_by_id(service_id)
        if not service:
            raise NotFoundException(f"Service {service_id} not found")

        service.update_health_status(status == ServiceStatus.HEALTHY, check_time)
        await self._session.flush()
        return service

    async def update(
        self,
        service_id: str,
        update_data: Dict[str, Any]
    ) -> Service:
        """Update service details."""
        service = await self.get_by_id(service_id)
        if not service:
            raise NotFoundException(f"Service {service_id} not found")

        for key, value in update_data.items():
            if hasattr(service, key):
                setattr(service, key, value)

        await self._session.flush()
        return service

    async def deactivate(self, service_id: str) -> Service:
        """Deactivate service."""
        service = await self.get_by_id(service_id)
        if not service:
            raise NotFoundException(f"Service {service_id} not found")

        service.is_active = False
        service.status = ServiceStatus.STOPPING
        await self._session.flush()
        return service

    async def delete(self, service_id: str) -> bool:
        """Delete service."""
        query = delete(Service).where(Service.id == service_id)
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def get_services_by_status(
        self,
        status: ServiceStatus
    ) -> List[Service]:
        """Get services by status."""
        query = select(Service).where(
            and_(
                Service.status == status,
                Service.is_active is True
            )
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_services_with_failing_health_checks(
        self,
        failure_threshold: int = 3
    ) -> List[Service]:
        """Get services with consecutive health check failures."""
        query = select(Service).where(
            and_(
                Service.consecutive_failures >= failure_threshold,
                Service.is_active is True
            )
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def reset_health_checks(self, service_id: str) -> None:
        """Reset health check failures counter."""
        service = await self.get_by_id(service_id)
        if not service:
            raise NotFoundException(f"Service {service_id} not found")

        service.consecutive_failures = 0
        await self._session.flush()
