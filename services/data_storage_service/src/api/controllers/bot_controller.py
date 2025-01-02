from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database_manager import DatabaseManager
from src.db.database import get_session
from src.db.repositories import BotRepository
from src.api.schemas import (
    BotCreate,
    BotResponse,
    BotUpdate,
    BotListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.integrations.auth_service import AuthService
from src.integrations.auth_service.client import get_current_user


class BotController:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        auth_service: AuthService = Depends(AuthService),
        database_manager: DatabaseManager = Depends(DatabaseManager)
    ):
        self.repository = BotRepository(session)
        self.auth_service = auth_service
        self.database_manager = database_manager

    @handle_exceptions
    async def create_bot(self, bot_data: BotCreate, current_user: dict = Depends(get_current_user)) -> BotResponse:
        """
        Creates a new bot in the database and generates a DSN for it.
        """
        logger.info(f"Creating bot with data: {bot_data}")
        try:
          bot = await self.repository.create(
              **bot_data.model_dump(), user_id=current_user['id']
          )
          logger.info(f"Bot created in database: {bot}")

          # Создаем базу данных для бота и получаем DSN
          try:
             dsn = await self.database_manager.create_database_for_bot(bot.id, current_user['id'])
             logger.info(f"Database created for bot {bot.id}, DSN: {dsn}")
          except Exception as e:
             logger.error(f"Failed to create database for bot {bot.id}. Rolling back. Error: {e}")
             await self.repository.delete(bot.id)  # Откатываем создание бота в случае ошибки
             raise HTTPException(
                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail=f"Failed to create database for bot. {str(e)}",
                ) from e
        
          bot_response = BotResponse(**bot.__dict__, dsn=dsn)
          logger.info(f"Bot created successfully. Response: {bot_response}")
          return bot_response
        except Exception as e:
          logger.error(f"Error creating bot: {e}")
          raise

    @handle_exceptions
    async def get_bot(self, bot_id: int, current_user: dict = Depends(get_current_user)) -> BotResponse:
        """
        Retrieves a bot by its ID and user_id.
        """
        logger.info(f"Getting bot with ID: {bot_id}")
        try:
          bot = await self.repository.get(bot_id=bot_id, user_id=current_user['id'])
          if not bot:
               logger.warning(f"Bot with ID {bot_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Bot with ID {bot_id} not found",
                )
        
          dsn = await self.database_manager.get_bot_dsn(bot_id)
          bot_response = BotResponse(**bot.__dict__, dsn=dsn)
          logger.info(f"Bot retrieved successfully: {bot_response}")
          return bot_response
        except Exception as e:
          logger.error(f"Error getting bot {bot_id}: {e}")
          raise


    @handle_exceptions
    async def get_all_bots(self, current_user: dict = Depends(get_current_user)) -> BotListResponse:
        """
        Retrieves all bots of the current user.
        """
        logger.info("Getting all bots")
        try:
          bots = await self.repository.get_all(user_id=current_user['id'])
          logger.info(f"Found {len(bots)} bots for user {current_user['id']}")
          bot_responses = []
          for bot in bots:
              dsn = await self.database_manager.get_bot_dsn(bot.id)
              bot_responses.append(BotResponse(**bot.__dict__, dsn=dsn))

          bot_list_response =  BotListResponse(items=bot_responses)
          logger.info(f"All bots retrieved successfully. Response: {bot_list_response}")
          return bot_list_response
        except Exception as e:
          logger.error(f"Error getting all bots: {e}")
          raise

    @handle_exceptions
    async def update_bot(self, bot_id: int, bot_data: BotUpdate, current_user: dict = Depends(get_current_user)) -> BotResponse:
        """
        Updates an existing bot.
        """
        logger.info(f"Updating bot with ID: {bot_id}, data: {bot_data}")
        try:
            bot = await self.repository.get(bot_id=bot_id, user_id=current_user['id'])
            if not bot:
                logger.warning(f"Bot with ID {bot_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bot with ID {bot_id} not found",
                )
            updated_bot = await self.repository.update(bot_id, **bot_data.model_dump(exclude_unset=True))
            dsn = await self.database_manager.get_bot_dsn(bot_id)
            bot_response = BotResponse(**updated_bot.__dict__, dsn=dsn)
            logger.info(f"Bot updated successfully: {bot_response}")
            return bot_response
        except Exception as e:
          logger.error(f"Error updating bot {bot_id}: {e}")
          raise

    @handle_exceptions
    async def delete_bot(self, bot_id: int, current_user: dict = Depends(get_current_user)) -> SuccessResponse:
        """
        Deletes a bot by its ID.
        """
        logger.info(f"Deleting bot with ID: {bot_id}")
        try:
            bot = await self.repository.get(bot_id=bot_id, user_id=current_user['id'])
            if not bot:
                logger.warning(f"Bot with ID {bot_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bot with ID {bot_id} not found",
                )

            await self.repository.delete(bot_id)
            logger.info(f"Bot {bot_id} deleted from database")
            await self.database_manager.delete_database_for_bot(bot_id)
            logger.info(f"Database for bot {bot_id} deleted")
            success_response = SuccessResponse(message="Bot deleted successfully")
            logger.info(f"Bot {bot_id} deleted successfully. Response: {success_response}")
            return success_response
        except Exception as e:
            logger.error(f"Error deleting bot {bot_id}: {e}")
            raise