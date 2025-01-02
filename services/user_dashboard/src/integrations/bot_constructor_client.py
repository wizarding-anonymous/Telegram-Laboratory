from typing import Dict, Optional
import httpx
from fastapi import HTTPException, status
from loguru import logger

from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.api.schemas import BotCreate, BotUpdate, BotResponse

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class BotConstructorClient:
    """
    Client for interacting with the Bot Constructor microservice.
    """

    def __init__(self):
        self.base_url = settings.BOT_CONSTRUCTOR_URL

    @handle_exceptions
    async def create_bot(self, bot_create: BotCreate, user_id: int) -> BotResponse:
        """
        Sends a request to the Bot Constructor service to create a new bot.
        """
        logger.info(f"Sending request to Bot Constructor to create bot for user {user_id} with data: {bot_create}")
        logging_client.info(f"Sending request to Bot Constructor to create bot for user {user_id} with data: {bot_create}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url=f"{self.base_url}/bots/", json=bot_create.model_dump(), timeout=10, headers={"user_id": str(user_id)}
                )
                response.raise_for_status()
                bot_data = response.json()
                logger.debug(f"Successfully created bot in Bot Constructor: {bot_data}")
                logging_client.debug(f"Successfully created bot in Bot Constructor: {bot_data}")
                return BotResponse(**bot_data)
            except httpx.HTTPError as e:
                logger.error(f"Error creating bot in Bot Constructor: {e}")
                logging_client.error(f"Error creating bot in Bot Constructor: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error communicating with Bot Constructor service: {e}",
                ) from e
            except Exception as e:
                 logger.error(f"An unexpected error occurred: {e}")
                 logging_client.error(f"An unexpected error occurred: {e}")
                 raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected error: {e}",
                ) from e

    @handle_exceptions
    async def update_bot(self, bot_id: int, bot_update: BotUpdate) -> BotResponse:
        """
         Sends a request to the Bot Constructor service to update an existing bot.
        """
        logger.info(f"Sending request to Bot Constructor to update bot with id: {bot_id}, data: {bot_update}")
        logging_client.info(f"Sending request to Bot Constructor to update bot with id: {bot_id}, data: {bot_update}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                   url=f"{self.base_url}/bots/{bot_id}", json=bot_update.model_dump(exclude_unset=True), timeout=10
                )
                response.raise_for_status()
                bot_data = response.json()
                logger.debug(f"Successfully updated bot in Bot Constructor: {bot_data}")
                logging_client.debug(f"Successfully updated bot in Bot Constructor: {bot_data}")
                return BotResponse(**bot_data)
            except httpx.HTTPError as e:
                logger.error(f"Error updating bot in Bot Constructor with id {bot_id}: {e}")
                logging_client.error(f"Error updating bot in Bot Constructor with id {bot_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error communicating with Bot Constructor service: {e}",
                ) from e
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                logging_client.error(f"An unexpected error occurred: {e}")
                raise HTTPException(
                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                     detail=f"Unexpected error: {e}",
                ) from e


    @handle_exceptions
    async def delete_bot(self, bot_id: int) -> None:
        """
        Sends a request to the Bot Constructor service to delete a bot.
        """
        logger.info(f"Sending request to Bot Constructor to delete bot with id {bot_id}")
        logging_client.info(f"Sending request to Bot Constructor to delete bot with id {bot_id}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    url=f"{self.base_url}/bots/{bot_id}", timeout=10
                )
                response.raise_for_status()
                logger.debug(f"Bot with ID {bot_id} deleted successfully in Bot Constructor")
                logging_client.debug(f"Bot with ID {bot_id} deleted successfully in Bot Constructor")
            except httpx.HTTPError as e:
                logger.error(f"Error deleting bot in Bot Constructor with id {bot_id}: {e}")
                logging_client.error(f"Error deleting bot in Bot Constructor with id {bot_id}: {e}")
                raise HTTPException(
                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                     detail=f"Error communicating with Bot Constructor service: {e}",
                ) from e
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                logging_client.error(f"An unexpected error occurred: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                     detail=f"Unexpected error: {e}",
                ) from e