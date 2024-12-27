import httpx
from loguru import logger
import os

class TelegramClient:
    """
    Client for interacting with the Telegram Bot API.
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
        logger.info("TelegramClient initialized")

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> dict:
        """
        Send a message to a Telegram chat.

        Args:
            chat_id (int): Chat ID to send the message to.
            text (str): Message text.
            parse_mode (str): Formatting style for the message (e.g., "Markdown", "HTML").

        Returns:
            dict: Response from the Telegram API.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send message: {response.text}")
                raise httpx.HTTPStatusError(
                    f"Error sending message: {response.status_code}",
                    request=response.request,
                    response=response,
                )
            logger.info(f"Message sent to chat {chat_id}: {text}")
            return response.json()

    async def set_webhook(self, webhook_url: str) -> dict:
        """
        Set a webhook for the Telegram bot.

        Args:
            webhook_url (str): The URL to receive Telegram updates.

        Returns:
            dict: Response from the Telegram API.
        """
        url = f"{self.base_url}/setWebhook"
        payload = {"url": webhook_url}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to set webhook: {response.text}")
                raise httpx.HTTPStatusError(
                    f"Error setting webhook: {response.status_code}",
                    request=response.request,
                    response=response,
                )
            logger.info(f"Webhook set: {webhook_url}")
            return response.json()

    async def delete_webhook(self) -> dict:
        """
        Delete the webhook for the Telegram bot.

        Returns:
            dict: Response from the Telegram API.
        """
        url = f"{self.base_url}/deleteWebhook"
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            if response.status_code != 200:
                logger.error(f"Failed to delete webhook: {response.text}")
                raise httpx.HTTPStatusError(
                    f"Error deleting webhook: {response.status_code}",
                    request=response.request,
                    response=response,
                )
            logger.info("Webhook deleted successfully")
            return response.json()

    async def get_updates(self, offset: int = 0, timeout: int = 10) -> dict:
        """
        Fetch updates from the Telegram API.

        Args:
            offset (int): Identifier of the first update to return.
            timeout (int): Timeout in seconds for long polling.

        Returns:
            dict: Response from the Telegram API.
        """
        url = f"{self.base_url}/getUpdates"
        params = {"offset": offset, "timeout": timeout}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"Failed to get updates: {response.text}")
                raise httpx.HTTPStatusError(
                    f"Error getting updates: {response.status_code}",
                    request=response.request,
                    response=response,
                )
            logger.info("Updates fetched successfully")
            return response.json()
