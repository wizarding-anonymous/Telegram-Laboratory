from typing import Any, Dict, Optional
from fastapi import HTTPException

from src.core.utils import handle_exceptions
from src.core.logic_manager.handlers.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.config import settings

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
         bot_logic: Dict[str, Any],
        current_block_id: int,
        user_message: str,
    ) -> Optional[int]:
         """Handles try-catch block."""
         content = block.get("content", {})
         logging_client.info(
            f"Handling try-catch block: {block.get('id')} for chat_id: {chat_id}"
         )
         from src.core.logic_manager.base import Block
         from src.core.logic_manager import LogicManager

         logic_manager = LogicManager()
         try:
             next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
             if next_blocks:
                 return next_blocks[0].get("id")
         except Exception as e:
            logging_client.error(f"An exception occurred in try block: {e}")
            catch_block_id = content.get("catch_block_id")
            if catch_block_id:
                from src.db.repositories import BlockRepository

                block_repository = BlockRepository()
                catch_block = await block_repository.get_by_id(catch_block_id)
                if catch_block:
                    return catch_block.id
                else:
                    logging_client.warning(
                        f"Catch block with id: {catch_block_id} was not found"
                    )
            else:
                logging_client.warning("Catch block was not defined in try block")
                return None
         return None

    @handle_exceptions
    async def handle_raise_error(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        user_message: str,
        bot_logic: Dict[str, Any],
    ) -> None:
        """Handles raise error block."""
        content = block.get("content", {})
        logging_client.info(f"Handling raise error block {block.get('id')}")
        message_template = content.get("message")
        if message_template:
            message = get_template(message_template).render(variables=variables)
            logging_client.error(f"Error raised by bot: {message}")
            raise HTTPException(status_code=400, detail=message)
        else:
            logging_client.warning("Error message was not provided")

    @handle_exceptions
    async def handle_handle_exception(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        bot_logic: Dict[str, Any],
         user_message: str
    ) -> Optional[int]:
        """Handles handle exception block."""
        content = block.get("content", {})
        logging_client.info(f"Handling handle exception block {block.get('id')}")
        exception_block_id = content.get("exception_block_id")
        if exception_block_id:
            from src.db.repositories import BlockRepository

            block_repository = BlockRepository()
            exception_block = await block_repository.get_by_id(exception_block_id)
            if exception_block:
                return exception_block.id
            else:
                logging_client.warning(
                    f"Exception block with id: {exception_block_id} was not found"
                )
        else:
            logging_client.warning("Exception block was not defined")
        return None