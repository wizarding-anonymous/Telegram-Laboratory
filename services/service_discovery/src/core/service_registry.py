from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session
from src.db.repositories import ServiceRepository
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class ServiceRegistry:
    """
    Manages service registrations in the Service Discovery.
    """

    def __init__(self, service_repository: ServiceRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = service_repository
        self.session = session

    @handle_exceptions
    async def register_service(self, name: str, address: str, port: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Registers a new service."""
        logging_client.info(f"Registering service: {name}, address: {address}, port: {port}")
        try:
           service = await self.repository.create(
               name=name, address=address, port=port, metadata=metadata
           )
           logging_client.info(f"Service registered successfully with id: {service.id}")
           return service.__dict__
        except Exception as e:
            logging_client.error(f"Error registering service {name}: {e}")
            raise

    @handle_exceptions
    async def get_service(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a service by its ID."""
        logging_client.info(f"Getting service with ID: {service_id}")
        try:
           service = await self.repository.get(service_id=service_id)
           if not service:
                logging_client.warning(f"Service with ID {service_id} not found")
                raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
                 )
           logging_client.info(f"Service with ID {service_id} retrieved successfully.")
           return service.__dict__
        except Exception as e:
            logging_client.error(f"Error getting service with ID: {service_id}. Error: {e}")
            raise


    @handle_exceptions
    async def get_all_services(self) -> List[Dict[str, Any]]:
        """Retrieves all registered services."""
        logging_client.info("Getting all services")
        try:
            services = await self.repository.get_all()
            logging_client.info(f"Successfully retrieved {len(services)} services.")
            return [service.__dict__ for service in services]
        except Exception as e:
           logging_client.error(f"Error getting all services: {e}")
           raise

    @handle_exceptions
    async def update_service(
        self,
        service_id: int,
        name: Optional[str] = None,
        address: Optional[str] = None,
        port: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing service."""
        logging_client.info(f"Updating service with ID: {service_id}")
        try:
            service = await self.repository.update(
                service_id=service_id, name=name, address=address, port=port, metadata=metadata
            )
            if not service:
                logging_client.warning(f"Service with id {service_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
                )
            logging_client.info(f"Service with ID {service_id} updated successfully")
            return service.__dict__
        except Exception as e:
             logging_client.error(f"Error updating service with ID {service_id}: {e}")
             raise

    @handle_exceptions
    async def unregister_service(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Unregisters a service by its ID."""
        logging_client.info(f"Unregistering service with ID: {service_id}")
        try:
            service = await self.repository.delete(service_id=service_id)
            if not service:
               logging_client.warning(f"Service with ID {service_id} not found for deletion")
               raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
                )
            logging_client.info(f"Service with ID {service_id} unregistered successfully.")
            return service.__dict__
        except Exception as e:
             logging_client.error(f"Error unregistering service with ID {service_id}: {e}")
             raise