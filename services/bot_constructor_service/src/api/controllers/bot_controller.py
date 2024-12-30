from typing import List, Optional

from fastapi import HTTPException, Depends, Query
from loguru import logger

from src.api.schemas import (
    BotCreate,
    BotUpdate,
    BotResponse,
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
)
from src.core.utils import (
    handle_exceptions,
    validate_bot_id,
    validate_bot_name,
    validate_version,
)
from src.db.repositories import BotRepository
from src.integrations.auth_service import get_current_user
from src.integrations.logging_client import LoggingClient
from src.integrations.telegram import TelegramClient
from src.core.utils.exceptions import BotNotFoundException, InvalidTokenException, InvalidBlockTypeException
from src.integrations.data_storage_client import DataStorageClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class BotController:
    """
    Controller for managing bots.
    """

    def __init__(
        self,
        bot_repository: BotRepository = Depends(),
        telegram_client: TelegramClient = Depends(),
         data_storage_client: DataStorageClient = Depends()
    ):
        self.bot_repository = bot_repository
        self.telegram_client = telegram_client
        self.data_storage_client = data_storage_client

    @handle_exceptions
    async def create_bot(
        self, bot_create: BotCreate, user: dict = Depends(get_current_user)
    ) -> BotResponse:
        """Creates a new bot."""
        logging_client.info(f"Creating bot with name: {bot_create.name}")

        validate_bot_name(bot_create.name)
        if "admin" not in user.get("roles", []):
            logging_client.warning(
                f"User with id: {user['id']} does not have permission to create bots"
            )
            raise HTTPException(status_code=403, detail="Permission denied")
        
        #Validate telegram token
        try:
            await self.telegram_client.validate_token(bot_create.token)
        except Exception as e:
           logging_client.error(f"Error when validate telegram token: {e}")
           raise InvalidTokenException(detail=str(e))
        
        if bot_create.library not in ["telegram_api", "aiogram", "telebot"]:
           logging_client.error(f"Invalid bot library: {bot_create.library}")
           raise InvalidBlockTypeException(block_type=bot_create.library)

        bot = await self.bot_repository.create(bot_create.model_dump(), user_id=user["id"])
        logging_client.info(f"Bot with id: {bot.id} created successfully")
        
        await self.data_storage_client.create_database_for_bot(bot_id=bot.id, user_id=user.get("id"))

        return BotResponse(**bot.model_dump())

    @handle_exceptions
    async def get_bot(
        self, bot_id: int, user: dict = Depends(get_current_user)
    ) -> BotResponse:
        """Gets a specific bot by id."""
        logging_client.info(f"Getting bot with id: {bot_id}")
        validate_bot_id(bot_id)
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
            logging_client.warning(f"Bot with id: {bot_id} not found")
            raise BotNotFoundException(bot_id=bot_id)

        if "admin" not in user.get("roles", []):
            logging_client.warning(
                f"User: {user['id']} does not have permission to get bots"
            )
            raise HTTPException(status_code=403, detail="Permission denied")
            
        logging_client.info(f"Bot with id: {bot_id} retrieved successfully")
        return BotResponse(**bot.model_dump())

    @handle_exceptions
    async def list_bots(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        user: dict = Depends(get_current_user)
    ) -> PaginatedResponse[BotResponse]:
        """Gets a list of bots for the user."""
        logging_client.info(f"Listing bots for user id: {user['id']}")
        if "admin" not in user.get("roles", []):
             logging_client.warning(f"User: {user['id']} does not have permission to list bots")
             raise HTTPException(status_code=403, detail="Permission denied")


        bots, total = await self.bot_repository.list_paginated(
            page=page, page_size=page_size, user_id=user["id"]
        )
        bot_list = [BotResponse(**bot.model_dump()) for bot in bots]
        logging_client.info(f"Found {len(bot_list)} bots for user id: {user['id']}")
        return PaginatedResponse(
            items=bot_list, page=page, page_size=page_size, total=total
        )

    @handle_exceptions
    async def update_bot(
        self, bot_id: int, bot_update: BotUpdate, user: dict = Depends(get_current_user)
    ) -> BotResponse:
        """Updates an existing bot."""
        logging_client.info(f"Updating bot with id: {bot_id}")
        validate_bot_id(bot_id)
        
        bot = await self.bot_repository.get_by_id(bot_id)

        if not bot:
            logging_client.warning(f"Bot with id: {bot_id} not found")
            raise BotNotFoundException(bot_id=bot_id)
        
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to update bots")
            raise HTTPException(status_code=403, detail="Permission denied")
            
        bot_data = bot_update.model_dump(exclude_unset=True)

        if bot_data.get("name"):
          validate_bot_name(bot_data.get("name"))
        if bot_data.get("version"):
          validate_version(bot_data.get("version"))
        
         #Validate telegram token
        if bot_data.get("token"):
            try:
                await self.telegram_client.validate_token(bot_data.get("token"))
            except Exception as e:
                logging_client.error(f"Error when validate telegram token: {e}")
                raise InvalidTokenException(detail=str(e))
        
        if bot_data.get("library"):
           if bot_data.get("library") not in ["telegram_api", "aiogram", "telebot"]:
              logging_client.error(f"Invalid bot library: {bot_data.get('library')}")
              raise InvalidBlockTypeException(block_type=bot_data.get("library"))


        updated_bot = await self.bot_repository.update(bot_id, bot_data)
        logging_client.info(f"Bot with id: {bot_id} updated successfully")
        return BotResponse(**updated_bot.model_dump())

    @handle_exceptions
    async def delete_bot(
        self, bot_id: int, user: dict = Depends(get_current_user)
    ) -> SuccessResponse:
        """Deletes a bot."""
        logging_client.info(f"Deleting bot with id: {bot_id}")
        validate_bot_id(bot_id)

        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
             logging_client.warning(f"Bot with id: {bot_id} not found")
             raise BotNotFoundException(bot_id=bot_id)

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to delete bots")
            raise HTTPException(status_code=403, detail="Permission denied")

        await self.bot_repository.delete(bot_id)
        logging_client.info(f"Bot with id: {bot_id} deleted successfully")
        
        await self.data_storage_client.delete_database_for_bot(bot_id=bot_id)

        return SuccessResponse(message="Bot deleted successfully")