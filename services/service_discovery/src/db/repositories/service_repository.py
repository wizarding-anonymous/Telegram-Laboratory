from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Service
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class ServiceRepository:
    """
    Repository for performing CRUD operations on the Service model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, name: str, address: str, port: int, metadata: dict) -> Service:
        """
        Creates a new service in the database.
        """
        logger.info(f"Creating service with name: {name}")
        try:
            service = Service(name=name, address=address, port=port, metadata=metadata)
            self.session.add(service)
            await self.session.commit()
            await self.session.refresh(service)
            logger.info(f"Service with name {name} created successfully with id: {service.id}")
            return service
        except Exception as e:
             logger.error(f"Error creating service with name {name}: {e}")
             raise DatabaseException(f"Failed to create service: {e}") from e


    @handle_exceptions
    async def get(self, service_id: int) -> Optional[Service]:
        """
        Retrieves a service by its ID.
        """
        logger.info(f"Getting service with ID: {service_id}")
        try:
            query = select(Service).where(Service.id == service_id)
            result = await self.session.execute(query)
            service = result.scalar_one_or_none()
            if service:
                logger.debug(f"Service with ID {service_id} found.")
            else:
                logger.warning(f"Service with ID {service_id} not found")
            return service
        except Exception as e:
            logger.error(f"Error getting service with id {service_id}: {e}")
            raise DatabaseException(f"Failed to get service with id {service_id}: {e}") from e


    @handle_exceptions
    async def get_all(self) -> List[Service]:
        """
        Retrieves all services.
        """
        logger.info("Getting all services")
        try:
            query = select(Service)
            result = await self.session.execute(query)
            services = list(result.scalars().all())
            logger.debug(f"Found {len(services)} services")
            return services
        except Exception as e:
             logger.error(f"Error getting all services: {e}")
             raise DatabaseException(f"Failed to get all services: {e}") from e


    @handle_exceptions
    async def update(self, service_id: int, name: Optional[str] = None, address: Optional[str] = None, port: Optional[int] = None, metadata: Optional[dict] = None) -> Optional[Service]:
        """
        Updates an existing service by its ID.
        """
        logger.info(f"Updating service with ID: {service_id}, name: {name}, address: {address}, port: {port}")
        try:
            query = select(Service).where(Service.id == service_id)
            result = await self.session.execute(query)
            service = result.scalar_one_or_none()
            if service:
                if name is not None:
                     service.name = name
                if address is not None:
                     service.address = address
                if port is not None:
                     service.port = port
                if metadata is not None:
                     service.metadata = metadata
                await self.session.commit()
                await self.session.refresh(service)
                logger.info(f"Service with ID {service_id} updated successfully")
            else:
                logger.warning(f"Service with ID {service_id} not found for update.")
            return service
        except Exception as e:
            logger.error(f"Error updating service with ID {service_id}: {e}")
            raise DatabaseException(f"Failed to update service with id {service_id}: {e}") from e

    @handle_exceptions
    async def delete(self, service_id: int) -> Optional[Service]:
        """
        Deletes a service by its ID.
        """
        logger.info(f"Deleting service with ID: {service_id}")
        try:
            query = delete(Service).where(Service.id == service_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Service with id {service_id} deleted successfully.")
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error deleting service with ID {service_id}: {e}")
            raise DatabaseException(f"Failed to delete service with id {service_id}: {e}") from e