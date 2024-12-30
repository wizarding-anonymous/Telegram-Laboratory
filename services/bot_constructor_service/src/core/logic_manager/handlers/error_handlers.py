# src/core/logic_manager/handlers/error_handlers.py
from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class ErrorHandler:
    """
    Handler for processing error handling blocks.
    """

    @handle_exceptions
    async def handle_try_catch(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any], next_block_id: int) -> Optional[int]:
        """
        Handles a try-catch block, returning next block id in try or catching errors.

        Args:
            block (dict): The try-catch block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
             variables (dict): Dictionary of variables.
             next_block_id (int): ID of next block, used only in "try" case

        Returns:
             Optional[int]: The ID of the next block to execute if try, or the error handler block if exception occurred
        """
        try_block_id = block.get("content", {}).get("try_block_id")
        catch_block_id = block.get("content", {}).get("catch_block_id")

        try:
           return next_block_id
        except Exception as e:
             logging_client.exception(f"Exception in try block: {e}")
             return catch_block_id

    @handle_exceptions
    async def handle_raise_error(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
      """
      Handles raising an error within the bot's logic.

      Args:
          block (dict): The raise error block details from the database.
          chat_id (int): Telegram chat ID where the interaction is happening.
          variables (dict): Dictionary of variables.
      """
      error_message = block.get("content", {}).get("message", "An error occurred")
      template = get_template(error_message)
      rendered_message = template.render(variables=variables)
      logging_client.error(f"Raised error: {rendered_message}")
      raise Exception(rendered_message)


    @handle_exceptions
    async def handle_exception(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any], exception: Exception) -> None:
        """
        Handles a caught exception and logs the error.

        Args:
           block (dict): The exception handling block details from database
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
           exception (Exception): The exception that was caught.
        """

        error_message = block.get("content", {}).get("message", "An error occurred")
        template = get_template(error_message)
        rendered_message = template.render(variables=variables)
        logging_client.error(f"Caught exception: {rendered_message}, original error: {exception}")

from src.core.logic_manager.handlers.utils import get_template