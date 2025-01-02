from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Integration
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class IntegrationRepository:
    """
    Repository for performing CRUD operations on the Integration model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, service: str, api_key: str, user_id: int) -> Integration:
        """
        Creates a new integration in the database.
        """
        logger.info(f"Creating integration: {service} for user {user_id}")
        try:
            integration = Integration(service=service, api_key=api_key, user_id=user_id)
            self.session.add(integration)
            await self.session.commit()
            await self.session.refresh(integration)
            logger.info(f"Integration created successfully with id: {integration.id}")
            return integration
        except Exception as e:
            logger.error(f"Error creating integration {service} for user {user_id}: {e}")
            raise DatabaseException(f"Failed to create integration {service}: {e}") from e

    @handle_exceptions
    async def get(self, integration_id: int, user_id: int) -> Optional[Integration]:
        """
        Retrieves an integration by its ID and user_id.
        """
        logger.info(f"Getting integration with ID: {integration_id} for user: {user_id}")
        try:
            query = select(Integration).where(Integration.id == integration_id, Integration.user_id == user_id)
            result = await self.session.execute(query)
            integration = result.scalar_one_or_none()
            if integration:
                 logger.debug(f"Integration with ID {integration_id} found")
            else:
                 logger.warning(f"Integration with ID {integration_id} not found")
            return integration
        except Exception as e:
            logger.error(f"Error getting integration {integration_id}: {e}")
            raise DatabaseException(f"Failed to get integration with id {integration_id}: {e}") from e

    @handle_exceptions
    async def get_all_by_user_id(self, user_id: int) -> List[Integration]:
        """
        Retrieves all integrations for a specific user ID.
        """
        logger.info(f"Getting all integrations for user ID: {user_id}")
        try:
           query = select(Integration).where(Integration.user_id == user_id)
           result = await self.session.execute(query)
           integrations = list(result.scalars().all())
           logger.debug(f"Found {len(integrations)} integrations for user {user_id}")
           return integrations
        except Exception as e:
             logger.error(f"Error getting all integrations for user {user_id}: {e}")
             raise DatabaseException(f"Failed to get all integrations for user {user_id}: {e}") from e

    @handle_exceptions
    async def update(self, integration_id: int, user_id: int, service: Optional[str] = None, api_key: Optional[str] = None) -> Optional[Integration]:
        """
        Updates an existing integration by its ID.
        """
        logger.info(f"Updating integration with ID: {integration_id}, service: {service}, user {user_id}")
        try:
            query = select(Integration).where(Integration.id == integration_id, Integration.user_id == user_id)
            result = await self.session.execute(query)
            integration = result.scalar_one_or_none()
            if integration:
                if service is not None:
                    integration.service = service
                if api_key is not None:
                    integration.api_key = api_key
                await self.session.commit()
                await self.session.refresh(integration)
                logger.info(f"Integration with ID {integration_id} updated successfully.")
            else:
                logger.warning(f"Integration with ID {integration_id} not found for update")
            return integration
        except Exception as e:
            logger.error(f"Error updating integration with ID {integration_id}: {e}")
            raise DatabaseException(f"Failed to update integration with id {integration_id}: {e}") from e

    @handle_exceptions
    async def delete(self, integration_id: int, user_id: int) -> Optional[Integration]:
        """
        Deletes a integration by its ID.
        """
        logger.info(f"Deleting integration with ID: {integration_id} for user_id: {user_id}")
        try:
            query = delete(Integration).where(Integration.id == integration_id, Integration.user_id == user_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Integration with ID {integration_id} deleted successfully for user {user_id}.")
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error deleting integration with id {integration_id}: {e}")
            raise DatabaseException(f"Failed to delete integration with id {integration_id}: {e}") from e