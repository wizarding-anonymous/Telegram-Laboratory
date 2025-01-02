from typing import List
from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.integration_manager import IntegrationManager
from src.api.schemas import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
    IntegrationListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.integrations.logging_client import LoggingClient
from src.api.middleware.auth import auth_required
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class IntegrationController:
    """
    Controller for handling integration-related operations for the User Dashboard.
    """

    def __init__(self, integration_manager: IntegrationManager = Depends(), session: AsyncSession = Depends(get_session)):
        self.integration_manager = integration_manager
        self.session = session

    @handle_exceptions
    async def create_integration(self, integration_data: IntegrationCreate, user: dict = Depends(auth_required)) -> IntegrationResponse:
        """
        Creates a new integration for a user.
        """
        logging_client.info(f"Creating new integration: {integration_data.service} for user {user['id']}")
        try:
            integration = await self.integration_manager.create_integration(
                **integration_data.model_dump(), user_id=user['id']
            )
            logging_client.info(f"Integration created successfully with ID: {integration.id}")
            return IntegrationResponse(**integration.__dict__)
        except Exception as e:
             logging_client.error(f"Failed to create integration: {e}")
             raise

    @handle_exceptions
    async def get_integration(self, integration_id: int, user: dict = Depends(auth_required)) -> IntegrationResponse:
        """
        Retrieves an integration by its ID.
        """
        logging_client.info(f"Getting integration with ID: {integration_id} for user {user['id']}")
        try:
            integration = await self.integration_manager.get_integration(integration_id=integration_id, user_id=user['id'])
            if not integration:
                 logging_client.warning(f"Integration with ID {integration_id} not found for user {user['id']}")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Integration with ID {integration_id} not found",
                 )
            logging_client.info(f"Integration with ID {integration_id} retrieved successfully for user: {user['id']}")
            return IntegrationResponse(**integration.__dict__)
        except Exception as e:
             logging_client.error(f"Failed to get integration {integration_id} for user {user['id']}: {e}")
             raise

    @handle_exceptions
    async def get_all_integrations(self, user: dict = Depends(auth_required)) -> IntegrationListResponse:
        """
        Retrieves a list of all integrations for the current user.
        """
        logging_client.info(f"Getting all integrations for user: {user['id']}")
        try:
            integrations = await self.integration_manager.get_all_integrations(user_id=user['id'])
            logging_client.info(f"Successfully retrieved {len(integrations)} integrations for user {user['id']}")
            return IntegrationListResponse(items=[IntegrationResponse(**integration.__dict__) for integration in integrations])
        except Exception as e:
             logging_client.error(f"Failed to get all integrations for user {user['id']}: {e}")
             raise

    @handle_exceptions
    async def update_integration(self, integration_id: int, integration_data: IntegrationUpdate, user: dict = Depends(auth_required)) -> IntegrationResponse:
        """
        Updates an existing integration.
        """
        logging_client.info(f"Updating integration with ID: {integration_id}, data: {integration_data} for user: {user['id']}")
        try:
            integration = await self.integration_manager.update_integration(
                integration_id=integration_id,  user_id=user['id'], **integration_data.model_dump(exclude_unset=True)
            )
            if not integration:
                logging_client.warning(f"Integration with ID {integration_id} not found for update for user {user['id']}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Integration with ID {integration_id} not found",
                 )
            logging_client.info(f"Integration with ID {integration_id} updated successfully for user {user['id']}")
            return IntegrationResponse(**integration.__dict__)
        except Exception as e:
           logging_client.error(f"Failed to update integration with id {integration_id} for user {user['id']}: {e}")
           raise

    @handle_exceptions
    async def delete_integration(self, integration_id: int, user: dict = Depends(auth_required)) -> SuccessResponse:
        """
        Deletes an integration by its ID.
        """
        logging_client.info(f"Deleting integration with ID: {integration_id} for user: {user['id']}")
        try:
            integration = await self.integration_manager.delete_integration(integration_id=integration_id, user_id=user['id'])
            if not integration:
                 logging_client.warning(f"Integration with ID {integration_id} not found for deletion for user {user['id']}")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Integration with ID {integration_id} not found",
                 )
            logging_client.info(f"Integration with ID {integration_id} deleted successfully for user: {user['id']}")
            return SuccessResponse(message="Integration deleted successfully")
        except Exception as e:
            logging_client.error(f"Failed to delete integration with id {integration_id} for user {user['id']}: {e}")
            raise