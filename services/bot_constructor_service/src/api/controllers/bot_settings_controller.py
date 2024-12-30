from fastapi import Depends, HTTPException

from src.api.schemas import (
    BotSettingsCreate,
    BotSettingsUpdate,
    BotSettingsResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions, validate_bot_id
from src.db.repositories import BotRepository
from src.integrations.auth_service import get_current_user
from src.integrations.logging_client import LoggingClient
from src.core.utils.exceptions import BotNotFoundException
from src.integrations.telegram import TelegramClient


logging_client = LoggingClient(service_name="bot_constructor")


class BotSettingsController:
    """
    Controller for managing bot settings.
    """

    def __init__(
        self,
        bot_repository: BotRepository = Depends(),
        telegram_client: TelegramClient = Depends(),
    ):
        self.bot_repository = bot_repository
        self.telegram_client = telegram_client


    @handle_exceptions
    async def create_bot_settings(
        self, bot_id: int, bot_settings: BotSettingsCreate, user: dict = Depends(get_current_user)
    ) -> BotSettingsResponse:
        """Creates settings for a specific bot."""
        logging_client.info(f"Creating bot settings for bot with id: {bot_id}")
        validate_bot_id(bot_id)

        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
             logging_client.warning(f"Bot with id: {bot_id} not found")
             raise BotNotFoundException(bot_id=bot_id)

        if "admin" not in user.get("roles", []):
            logging_client.warning(
                f"User with id: {user.get('id')} has not admin rights"
            )
            raise HTTPException(status_code=403, detail="Admin role required")
        
        #Validate telegram token
        try:
            await self.telegram_client.validate_token(bot_settings.token)
        except Exception as e:
             logging_client.error(f"Error when validate telegram token: {e}")
             raise HTTPException(status_code=400, detail=f"Telegram token is invalid: {e}")

        bot_data = bot_settings.model_dump()
        updated_bot = await self.bot_repository.update(bot_id, bot_data)
        
        logging_client.info(f"Bot settings with bot_id: {bot_id} created successfully")
        return BotSettingsResponse(**updated_bot.model_dump())

    @handle_exceptions
    async def get_bot_settings(
        self, bot_id: int, user: dict = Depends(get_current_user)
    ) -> BotSettingsResponse:
        """Gets the settings of a specific bot."""
        logging_client.info(f"Getting bot settings for bot with id: {bot_id}")
        validate_bot_id(bot_id)

        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
            logging_client.warning(f"Bot with id: {bot_id} not found")
            raise BotNotFoundException(bot_id=bot_id)

        if "admin" not in user.get("roles", []):
             logging_client.warning(f"User with id: {user.get('id')} does not have permission to get bot settings")
             raise HTTPException(status_code=403, detail="Permission denied")
        
        logging_client.info(f"Bot settings with bot_id: {bot_id} retrieved successfully")
        return BotSettingsResponse(**bot.model_dump())


    @handle_exceptions
    async def update_bot_settings(
        self, bot_id: int, bot_settings: BotSettingsUpdate, user: dict = Depends(get_current_user)
    ) -> BotSettingsResponse:
        """Updates the settings of a specific bot."""
        logging_client.info(f"Updating bot settings for bot with id: {bot_id}")
        validate_bot_id(bot_id)
        
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
            logging_client.warning(f"Bot with id: {bot_id} not found")
            raise BotNotFoundException(bot_id=bot_id)

        if "admin" not in user.get("roles", []):
             logging_client.warning(f"User with id: {user.get('id')} does not have permission to update bot settings")
             raise HTTPException(status_code=403, detail="Permission denied")
        
         #Validate telegram token
        if bot_settings.token:
           try:
               await self.telegram_client.validate_token(bot_settings.token)
           except Exception as e:
                logging_client.error(f"Error when validate telegram token: {e}")
                raise HTTPException(status_code=400, detail=f"Telegram token is invalid: {e}")
    
        bot_data = bot_settings.model_dump(exclude_unset=True)
        updated_bot = await self.bot_repository.update(bot_id, bot_data)
        logging_client.info(f"Bot settings with bot_id: {bot_id} updated successfully")
        return BotSettingsResponse(**updated_bot.model_dump())
    
    
    @handle_exceptions
    async def delete_bot_settings(
        self, bot_id: int, user: dict = Depends(get_current_user)
    ) -> SuccessResponse:
        """Deletes the settings of a specific bot."""
        logging_client.info(f"Deleting bot settings for bot with id: {bot_id}")
        validate_bot_id(bot_id)
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
           logging_client.warning(f"Bot with id: {bot_id} not found")
           raise BotNotFoundException(bot_id=bot_id)
        
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user.get('id')} does not have permission to delete bot settings")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        bot_data = {"token": "", "library": "telegram_api"}
        await self.bot_repository.update(bot_id, bot_data)
        logging_client.info(f"Bot settings with bot_id: {bot_id} deleted successfully")
        return SuccessResponse(message="Bot settings deleted successfully")