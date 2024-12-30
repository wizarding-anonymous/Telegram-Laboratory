from typing import List, Dict, Any
from src.core.utils import handle_exceptions
from src.integrations.telegram.client import TelegramClient
from src.core.utils import validate_callback_data
from src.core.logic_manager.handlers.utils import get_template

class CallbackHandler:
    """
    Handler for processing callback query blocks.
    """

    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client


    @handle_exceptions
    async def handle_callback_query(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> str:
        """
        Handles an incoming callback query.

        Args:
            block (dict): The callback query block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.

        Returns:
             str: callback query data
        """
        callback_data = block.get("content", {}).get("data")
        validate_callback_data(callback_data)
        template = get_template(callback_data)
        rendered_callback_data = template.render(variables=variables)
        return rendered_callback_data


    @handle_exceptions
    async def handle_send_callback_response(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
         """
         Sends a response to a callback query.

         Args:
            block (dict): The callback response block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
         """
         text = block.get("content", {}).get("text")

         if text:
             template = get_template(text)
             rendered_text = template.render(variables=variables)
             await self.telegram_client.answer_callback_query(
                 callback_query_id=variables.get("callback_query_id"), text=rendered_text
             )