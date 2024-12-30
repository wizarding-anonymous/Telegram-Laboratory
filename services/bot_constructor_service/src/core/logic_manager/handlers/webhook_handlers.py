from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.telegram.client import TelegramClient
from src.core.utils import validate_webhook_url

class WebhookHandler:
    """
    Handler for processing webhook blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_set_webhook(self, block: Dict[str, Any], bot_token:str,  chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Sets a webhook for a bot.

        Args:
            block (dict): The set webhook block details from database.
            bot_token (str): Telegram bot token
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        webhook_url = block.get("content", {}).get("url")
        validate_webhook_url(webhook_url)

        await self.telegram_client.set_webhook(bot_token=bot_token, url=webhook_url)

    @handle_exceptions
    async def handle_delete_webhook(self, block: Dict[str, Any], bot_token:str,  chat_id: int, variables: Dict[str,Any]) -> None:
         """
         Deletes the webhook for the bot.

         Args:
            block (dict): The delete webhook block details from database.
            bot_token (str): Telegram bot token
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
         """
         await self.telegram_client.delete_webhook(bot_token=bot_token)