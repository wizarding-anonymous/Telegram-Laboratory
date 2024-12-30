from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.telegram.client import TelegramClient

class PollingHandler:
    """
    Handler for processing polling blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_start_polling(self, block: Dict[str, Any], bot_token:str , chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Starts polling for updates.

        Args:
           block (dict): The start polling block details from database.
           bot_token (str): telegram bot token
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        
        await self.telegram_client.start_polling(bot_token=bot_token)


    @handle_exceptions
    async def handle_stop_polling(self, block: Dict[str, Any], bot_token:str, chat_id: int, variables: Dict[str,Any]) -> None:
         """
        Stops polling for updates.

        Args:
           block (dict): The stop polling block details from database.
           bot_token (str): telegram bot token
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
         await self.telegram_client.stop_polling(bot_token=bot_token)