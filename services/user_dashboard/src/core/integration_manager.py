from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.db.repositories import IntegrationRepository
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.core.utils.exceptions import ValidationException

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class IntegrationManager:
    """
    Manages integration-related business logic.
    """

    def __init__(self, integration_repository: IntegrationRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = integration_repository
        self.session = session

    @handle_exceptions
    async def create_integration(self, service: str, api_key: str, user_id: int) -> Dict[str, Any]:
        """
        Creates a new integration for a user.
        """
        logging_client.info(f"Creating new integration: {service} for user: {user_id}")

        if not service or not api_key:
            logging_client.warning("Service or API key cannot be empty")
            raise ValidationException("Service and API key are required")
        try:
            integration = await self.repository.create(
               service=service, api_key=api_key, user_id=user_id
            )
            logging_client.info(f"Integration created successfully with ID: {integration.id}")
            return integration.__dict__
        except Exception as e:
            logging_client.error(f"Error creating integration {service}: {e}")
            raise


    @handle_exceptions
    async def get_integration(self, integration_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an integration by its ID.
        """
        logging_client.info(f"Getting integration with ID: {integration_id} for user: {user_id}")
        try:
            integration = await self.repository.get(integration_id=integration_id, user_id=user_id)
            if not integration:
                 logging_client.warning(f"Integration with ID {integration_id} not found for user {user_id}")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
                 )
            logging_client.info(f"Integration with ID {integration_id} retrieved successfully for user: {user_id}")
            return integration.__dict__
        except Exception as e:
             logging_client.error(f"Error getting integration with ID {integration_id} for user: {user_id}: {e}")
             raise

    @handle_exceptions
    async def get_all_integrations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all integrations for the given user.
        """
        logging_client.info(f"Getting all integrations for user: {user_id}")
        try:
            integrations = await self.repository.get_all_by_user_id(user_id=user_id)
            logging_client.info(f"Successfully retrieved {len(integrations)} integrations for user {user_id}")
            return [integration.__dict__ for integration in integrations]
        except Exception as e:
             logging_client.error(f"Error getting all integrations for user {user_id}: {e}")
             raise
         

    @handle_exceptions
    async def update_integration(
        self,
        integration_id: int,
        user_id: int,
        service: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing integration.
        """
        logging_client.info(f"Updating integration with ID: {integration_id}, user {user_id}")
        try:
           integration = await self.repository.update(
                integration_id=integration_id, user_id=user_id, service=service, api_key=api_key
            )
           if not integration:
               logging_client.warning(f"Integration with ID {integration_id} not found for user {user_id}")
               raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
                )
           logging_client.info(f"Integration with ID {integration_id} updated successfully for user {user_id}")
           return integration.__dict__
        except Exception as e:
           logging_client.error(f"Error updating integration {integration_id}: {e}")
           raise


    @handle_exceptions
    async def delete_integration(self, integration_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Deletes an integration by its ID.
        """
        logging_client.info(f"Deleting integration with ID: {integration_id} for user: {user_id}")
        try:
            integration = await self.repository.delete(integration_id=integration_id, user_id=user_id)
            if not integration:
                logging_client.warning(f"Integration with id {integration_id} not found for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found"
                 )
            logging_client.info(f"Integration with ID {integration_id} deleted successfully for user: {user_id}")
            return integration.__dict__
        except Exception as e:
             logging_client.error(f"Error deleting integration with ID {integration_id} for user {user_id}: {e}")
             raise