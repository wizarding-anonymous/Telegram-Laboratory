from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.db.repositories import BotRepository
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.api.schemas import BotCreate, BotUpdate

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class BotManager:
    """
    Manages bot-related business logic in the User Dashboard.
    """

    def __init__(self, bot_repository: BotRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = bot_repository
        self.session = session

    @handle_exceptions
    async def create_bot(self, bot_data: BotCreate, user_id: int) -> Dict[str, Any]:
        """
        Creates a new bot for a specific user.
        """
        logging_client.info(f"Creating bot with name: {bot_data.name} for user: {user_id}")
        try:
            bot = await self.repository.create(**bot_data.model_dump(), user_id=user_id)
            logging_client.info(f"Bot created successfully with ID: {bot.id}")
            return bot.__dict__
        except Exception as e:
            logging_client.error(f"Error creating bot with name {bot_data.name}: {e}")
            raise

    @handle_exceptions
    async def get_bot(self, bot_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a bot by its ID and user ID.
        """
        logging_client.info(f"Getting bot with ID: {bot_id} for user: {user_id}")
        try:
          bot = await self.repository.get(bot_id=bot_id, user_id=user_id)
          if not bot:
              logging_client.warning(f"Bot with ID {bot_id} not found for user: {user_id}")
              raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail="Bot not found",
                )
          logging_client.info(f"Bot with ID {bot_id} retrieved successfully for user: {user_id}")
          return bot.__dict__
        except Exception as e:
             logging_client.error(f"Error getting bot {bot_id} for user {user_id}: {e}")
             raise
        

    @handle_exceptions
    async def get_all_bots(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all bots for a specific user.
        """
        logging_client.info(f"Getting all bots for user: {user_id}")
        try:
           bots = await self.repository.get_all_by_user_id(user_id=user_id)
           logging_client.info(f"Successfully retrieved {len(bots)} bots for user: {user_id}")
           return [bot.__dict__ for bot in bots]
        except Exception as e:
           logging_client.error(f"Error getting all bots for user {user_id}: {e}")
           raise

    @handle_exceptions
    async def update_bot(
        self, bot_id: int, bot_data: BotUpdate, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing bot.
        """
        logging_client.info(f"Updating bot with ID: {bot_id}, data: {bot_data} for user: {user_id}")
        try:
            bot = await self.repository.update(
                bot_id=bot_id, **bot_data.model_dump(exclude_unset=True) , user_id=user_id
            )
            if not bot:
                logging_client.warning(f"Bot with ID {bot_id} not found for update for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found"
                 )
            logging_client.info(f"Bot with ID {bot_id} updated successfully for user {user_id}")
            return bot.__dict__
        except Exception as e:
            logging_client.error(f"Error updating bot {bot_id} for user {user_id}: {e}")
            raise

    @handle_exceptions
    async def delete_bot(self, bot_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Deletes a bot by its ID.
        """
        logging_client.info(f"Deleting bot with ID: {bot_id} for user: {user_id}")
        try:
            bot = await self.repository.delete(bot_id=bot_id, user_id=user_id)
            if not bot:
               logging_client.warning(f"Bot with ID {bot_id} not found for user {user_id}")
               raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found"
                )
            logging_client.info(f"Bot with ID {bot_id} deleted successfully for user {user_id}")
            return bot.__dict__
        except Exception as e:
            logging_client.error(f"Error deleting bot {bot_id} for user {user_id}: {e}")
            raise