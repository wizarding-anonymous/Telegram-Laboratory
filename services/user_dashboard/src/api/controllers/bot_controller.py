from typing import List, Optional
from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.bot_manager import BotManager
from src.api.schemas import (
    BotResponse,
    BotCreate,
    BotUpdate,
    BotListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.integrations.auth_service_client import AuthService
from src.api.middleware.auth import auth_required
from src.db.database import get_session
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.integrations.bot_constructor_client import BotConstructorClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class BotController:
    """
    Controller for handling bot-related operations in the User Dashboard microservice.
    """

    def __init__(self, 
                 bot_manager: BotManager = Depends(),
                 session: AsyncSession = Depends(get_session),
                 auth_service: AuthService = Depends(),
                 bot_constructor_client: BotConstructorClient = Depends()
    ):
        self.bot_manager = bot_manager
        self.auth_service = auth_service
        self.session = session
        self.bot_constructor_client = bot_constructor_client


    @handle_exceptions
    async def create_bot(self, bot_data: BotCreate, user: dict = Depends(auth_required)) -> BotResponse:
        """
        Creates a new bot for the authenticated user.
        """
        logging_client.info(f"Creating bot with data: {bot_data.name} for user {user.get('id')}")
        try:
            bot = await self.bot_manager.create_bot(bot_data=bot_data, user_id=user.get('id'))
            logging_client.info(f"Bot created successfully with id: {bot.id}")
            
            # Call Bot Constructor service to create a new bot with same data
            bot_constructor_bot = await self.bot_constructor_client.create_bot(
              bot_create=bot_data, user_id=user.get("id")
             )

            logging_client.info(f"Bot created in Bot Constructor with id {bot_constructor_bot.id}")
            return BotResponse(**bot.model_dump())
        except Exception as e:
            logging_client.error(f"Failed to create bot: {e}")
            raise


    @handle_exceptions
    async def get_bot(self, bot_id: int, user: dict = Depends(auth_required)) -> BotResponse:
        """
        Retrieves a bot by its ID for the authenticated user.
        """
        logging_client.info(f"Getting bot with ID: {bot_id} for user {user['id']}")
        try:
          bot = await self.bot_manager.get_bot(bot_id=bot_id, user_id=user['id'])
          if not bot:
            logging_client.warning(f"Bot with ID {bot_id} not found for user: {user['id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bot with ID {bot_id} not found",
                )
          logging_client.info(f"Bot with ID: {bot_id} retrieved successfully for user: {user['id']}")
          return BotResponse(**bot.model_dump())
        except Exception as e:
            logging_client.error(f"Failed to get bot {bot_id}: {e}")
            raise


    @handle_exceptions
    async def get_all_bots(self, user: dict = Depends(auth_required)) -> BotListResponse:
        """
        Retrieves all bots for the current user.
        """
        logging_client.info(f"Getting all bots for user: {user['id']}")
        try:
            bots = await self.bot_manager.get_all_bots(user_id=user['id'])
            logging_client.info(f"Successfully retrieved {len(bots)} bots for user {user['id']}")
            return BotListResponse(items=[BotResponse(**bot.model_dump()) for bot in bots])
        except Exception as e:
            logging_client.error(f"Failed to get all bots for user {user['id']}: {e}")
            raise

    @handle_exceptions
    async def update_bot(self, bot_id: int, bot_data: BotUpdate, user: dict = Depends(auth_required)) -> BotResponse:
        """
        Updates an existing bot.
        """
        logging_client.info(f"Updating bot with ID: {bot_id}, data: {bot_data} for user: {user['id']}")
        try:
             bot = await self.bot_manager.update_bot(
                bot_id=bot_id, bot_data=bot_data, user_id=user['id']
             )
             if not bot:
                 logging_client.warning(f"Bot with id: {bot_id} not found for user: {user['id']}")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bot with id {bot_id} not found",
                  )

             # Call Bot Constructor service to update the bot
             bot_constructor_bot = await self.bot_constructor_client.update_bot(
                 bot_id=bot_id, bot_update=bot_data
             )
             logging_client.info(f"Bot updated in Bot Constructor with id {bot_constructor_bot.id}")
             logging_client.info(f"Bot with ID {bot_id} updated successfully for user {user['id']}")
             return BotResponse(**bot.model_dump())
        except Exception as e:
           logging_client.error(f"Failed to update bot {bot_id} for user {user['id']}: {e}")
           raise

    @handle_exceptions
    async def delete_bot(self, bot_id: int, user: dict = Depends(auth_required)) -> SuccessResponse:
        """
        Deletes a bot by its ID.
        """
        logging_client.info(f"Deleting bot with ID: {bot_id} for user: {user['id']}")
        try:
             bot = await self.bot_manager.delete_bot(bot_id=bot_id, user_id=user['id'])
             if not bot:
                  logging_client.warning(f"Bot with id: {bot_id} not found for user: {user['id']}")
                  raise HTTPException(
                      status_code=status.HTTP_404_NOT_FOUND,
                      detail=f"Bot with id {bot_id} not found",
                    )
             # Call Bot Constructor service to delete the bot
             await self.bot_constructor_client.delete_bot(bot_id=bot_id)
             logging_client.info(f"Bot deleted in Bot Constructor with id {bot_id}")

             logging_client.info(f"Bot with ID {bot_id} deleted successfully for user {user['id']}")
             return SuccessResponse(message="Bot deleted successfully")
        except Exception as e:
             logging_client.error(f"Failed to delete bot with ID {bot_id} for user: {user['id']}: {e}")
             raise