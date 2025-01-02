from typing import List, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.repositories import ServiceRepository
from src.api.schemas import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
    ServiceListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.api.middleware.auth import admin_required


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class ServiceController:
    """
    Controller for managing service registrations in the Service Discovery.
    """

    def __init__(self, service_repository: ServiceRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = service_repository
        self.session = session

    @handle_exceptions
    async def register_service(self, service_data: ServiceCreate, user: dict = Depends(admin_required)) -> ServiceResponse:
        """
        Registers a new service.
        """
        logging_client.info(f"Registering new service: {service_data.name}")
        try:
            service = await self.repository.create(**service_data.model_dump())
            logging_client.info(f"Service registered successfully with ID: {service.id}")
            return ServiceResponse(**service.__dict__)
        except Exception as e:
            logging_client.error(f"Failed to register service: {e}")
            raise

    @handle_exceptions
    async def get_service(self, service_id: int, user: dict = Depends(admin_required)) -> ServiceResponse:
        """
        Retrieves a specific service by its ID.
        """
        logging_client.info(f"Getting service with ID: {service_id}")
        try:
           service = await self.repository.get(service_id=service_id)
           if not service:
               logging_client.warning(f"Service with ID {service_id} not found")
               raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
               )
           logging_client.info(f"Service with ID: {service_id} retrieved successfully")
           return ServiceResponse(**service.__dict__)
        except Exception as e:
            logging_client.error(f"Error getting service {service_id}: {e}")
            raise

    @handle_exceptions
    async def get_all_services(self, user: dict = Depends(admin_required)) -> ServiceListResponse:
        """
        Retrieves a list of all registered services.
        """
        logging_client.info("Getting all services")
        try:
            services = await self.repository.get_all()
            logging_client.info(f"Successfully retrieved {len(services)} services")
            return ServiceListResponse(
                items=[ServiceResponse(**service.__dict__) for service in services]
            )
        except Exception as e:
             logging_client.error(f"Failed to get all services: {e}")
             raise

    @handle_exceptions
    async def update_service(self, service_id: int, service_data: ServiceUpdate, user: dict = Depends(admin_required)) -> ServiceResponse:
        """
        Updates an existing service.
        """
        logging_client.info(f"Updating service with ID: {service_id}, data: {service_data}")
        try:
            service = await self.repository.update(
                service_id=service_id, **service_data.model_dump(exclude_unset=True)
            )
            if not service:
                logging_client.warning(f"Service with ID {service_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
                )
            logging_client.info(f"Service with ID {service_id} updated successfully")
            return ServiceResponse(**service.__dict__)
        except Exception as e:
           logging_client.error(f"Failed to update service {service_id}: {e}")
           raise

    @handle_exceptions
    async def delete_service(self, service_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Deletes a service by its ID.
        """
        logging_client.info(f"Deleting service with ID: {service_id}")
        try:
            service = await self.repository.delete(service_id=service_id)
            if not service:
               logging_client.warning(f"Service with ID {service_id} not found for deletion")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
                )
            logging_client.info(f"Service with ID {service_id} deleted successfully.")
            return SuccessResponse(message="Service unregistered successfully")
        except Exception as e:
           logging_client.error(f"Failed to delete service with ID {service_id}: {e}")
           raise