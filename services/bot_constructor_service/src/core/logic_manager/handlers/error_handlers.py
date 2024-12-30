from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from fastapi import HTTPException

from src.core.logic_manager.handlers.utils import get_template

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class ErrorHandler:
    """
    Handler for processing error handling blocks.
    """

    def __init__(self):
      pass

    @handle_exceptions
    async def handle_try_catch(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        next_block_id: Optional[int],
        bot_logic: Dict[str, Any],
        user_message: str,
    ) -> Optional[int]:
        """
        Handles a try-catch block, returning next block id in try or catching errors.

        Args:
            block (dict): The try-catch block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
            next_block_id (Optional[int]): ID of the next block, used only in the "try" case.
            bot_logic: Dict of bot logic.
            user_message: Incoming user message.

        Returns:
            Optional[int]: The ID of the next block to execute if try is successful,
                            or the error handler block if an exception occurred.
        """
        content = block.get("content", {})
        try_block_id = content.get("try_block_id")
        catch_block_id = content.get("catch_block_id")

        logging_client.info(f"Handling try-catch block for block id: {block.get('id')}")
        
        if not try_block_id:
           logging_client.warning(f"Try block id was not defined for block id {block.get('id')}")
           return catch_block_id if catch_block_id else None

        if next_block_id:
            from src.core.logic_manager import LogicManager

            logic_manager = LogicManager()
            try:
                next_blocks = await logic_manager._get_next_blocks(
                    block.get("id"), bot_logic
                )
                if next_blocks:
                    return next_blocks[0].get("id")
            except Exception as e:
                logging_client.exception(f"Exception in try block: {e}")
                return catch_block_id if catch_block_id else None

        return None

    @handle_exceptions
    async def handle_raise_error(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any], user_message: str, bot_logic: Dict[str, Any]
    ) -> None:
        """
        Handles raising an error within the bot's logic.

        Args:
            block (dict): The raise error block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
            bot_logic: Dict of bot logic.
            user_message: Incoming user message.
        """
        content = block.get("content", {})
        error_message = content.get("message", "An error occurred")
        if error_message:
            template = get_template(error_message)
            rendered_message = template.render(variables=variables)
            logging_client.error(f"Raised error: {rendered_message}")
            raise HTTPException(status_code=400, detail=rendered_message)
        else:
            logging_client.warning("Error message was not provided")


    @handle_exceptions
    async def handle_handle_exception(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        exception: Exception,
        bot_logic: Dict[str, Any],
        user_message: str
    ) -> Optional[int]:
        """
        Handles a caught exception and logs the error and executes exception block.

        Args:
           block (dict): The exception handling block details from database
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
           exception (Exception): The exception that was caught.
           bot_logic: Dict of bot logic.
           user_message: Incoming user message.
        """
        content = block.get("content", {})
        exception_block_id = content.get("exception_block_id")

        logging_client.info(f"Handling exception block with id: {block.get('id')}")
        if not exception_block_id:
            logging_client.warning("Exception block was not defined")
            return None

        error_message = content.get("message", "An error occurred")
        if error_message:
            template = get_template(error_message)
            rendered_message = template.render(variables=variables)
            logging_client.error(
                f"Caught exception: {rendered_message}, original error: {exception}"
            )
        else:
            logging_client.error(f"Caught exception: original error: {exception}")
        from src.core.logic_manager import LogicManager
        logic_manager = LogicManager()
        from src.db.repositories import BlockRepository

        block_repository = BlockRepository()
        exception_block = await block_repository.get_by_id(exception_block_id)
        if exception_block:
            return exception_block.id
        else:
            logging_client.warning(
                f"Exception block with id: {exception_block_id} was not found"
            )
        return None