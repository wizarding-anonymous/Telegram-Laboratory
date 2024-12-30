import httpx
from loguru import logger
import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from fastapi import HTTPException

from src.core.utils.exceptions import TelegramAPIException
from src.config import settings
from src.integrations import get_telegram_client


class TelegramClient(ABC):
    """
    Abstract base class for interacting with the Telegram Bot API.
    """

    def __init__(self, bot_token: str = None):
        """
        Initialize the TelegramClient.

        Args:
            bot_token (str): Telegram bot token. If not provided, loads from environment variable TELEGRAM_BOT_TOKEN.
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("Telegram bot token is required")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        logger.info(f"{self.__class__.__name__} initialized")

    async def validate_token(self, token: str) -> bool:
        """
        Validate telegram token.

        Args:
            token(str): Token for telegram bot.
        """
        url = f"https://api.telegram.org/bot{token}/getMe"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                if response.status_code == 200:
                    logger.info("Telegram token is valid")
                    return True
                else:
                    logger.error(
                        f"Telegram token is invalid, status_code: {response.status_code}"
                    )
                    return False
            except httpx.HTTPError as e:
                logger.error(f"Telegram token is invalid, exception: {e}")
                raise TelegramAPIException(detail=f"Telegram token is invalid: {e}")

    async def make_api_request(
        self,
        url: str,
        method: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Makes a request to Telegram API using a specific URL and method.

        Args:
           url (str): URL of the API endpoint.
           method (str): HTTP method (GET, POST, etc.).
           json (Optional[dict]): JSON payload if required.
           params (Optional[dict]): Query parameters if required.

        Returns:
            dict: Response from the Telegram API.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method, url=url, json=json, params=params
                )
                response.raise_for_status()
                logger.info(f"Telegram API request successful to {url}")
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Telegram API request failed to {url}: {e}")
                raise TelegramAPIException(
                    detail=f"Telegram API request failed to {url}: {e}"
                )
            except Exception as e:
                logger.error(f"Telegram API request failed to {url}: {e}")
                raise TelegramAPIException(
                    detail=f"Telegram API request failed to {url}: {e}"
                )

    @abstractmethod
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Any] = None,
        inline_keyboard: Optional[Any] = None,
    ) -> dict:
        """Abstract method for sending a message to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_photo(
        self, chat_id: int, photo_url: str, caption: Optional[str] = None
    ) -> dict:
        """Abstract method for sending a photo to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_video(
        self, chat_id: int, video_url: str, caption: Optional[str] = None
    ) -> dict:
        """Abstract method for sending a video to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_audio(
        self, chat_id: int, audio_url: str, caption: Optional[str] = None
    ) -> dict:
        """Abstract method for sending audio to Telegram chat"""
        raise NotImplementedError

    @abstractmethod
    async def send_document(
        self, chat_id: int, document_url: str, caption: Optional[str] = None
    ) -> dict:
        """Abstract method for sending a document to Telegram chat"""
        raise NotImplementedError

    @abstractmethod
    async def send_location(self, chat_id: int, latitude: float, longitude: float) -> dict:
        """Abstract method for sending location to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_sticker(self, chat_id: int, sticker_url: str) -> dict:
        """Abstract method for sending a sticker to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_contact(
        self, chat_id: int, phone_number: str, first_name: str, last_name: str = ""
    ) -> dict:
        """Abstract method for sending a contact to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_venue(
        self, chat_id: int, latitude: float, longitude: float, title: str, address: str
    ) -> dict:
        """Abstract method for sending a venue to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_game(self, chat_id: int, game_short_name: str) -> dict:
        """Abstract method for sending a game to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def send_poll(self, chat_id: int, question: str, options: List[str]) -> dict:
        """Abstract method for sending a poll to a Telegram chat."""
        raise NotImplementedError

    @abstractmethod
    async def set_webhook(self, bot_token:str, webhook_url: str) -> dict:
        """Abstract method for setting a webhook to a Telegram bot."""
        raise NotImplementedError

    @abstractmethod
    async def delete_webhook(self, bot_token:str) -> dict:
        """Abstract method for deleting a webhook from a Telegram bot."""
        raise NotImplementedError

    @abstractmethod
    async def get_updates(self, bot_token:str, offset: int = 0, timeout: int = 10) -> dict:
        """Abstract method for fetching updates from a Telegram bot."""
        raise NotImplementedError

    @abstractmethod
    async def handle_message(self, message: dict, bot_token: str) -> None:
        """Abstract method for handling incoming messages"""
        raise NotImplementedError

    @classmethod
    def get_client(cls) -> "TelegramClient":
         """
         Returns instance of telegram client depending on TELEGRAM_BOT_LIBRARY variable.
         """
         library = settings.TELEGRAM_BOT_LIBRARY
         return get_telegram_client(library)