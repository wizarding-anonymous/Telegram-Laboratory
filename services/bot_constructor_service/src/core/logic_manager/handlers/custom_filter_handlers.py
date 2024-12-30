from typing import Any, Dict, Optional
from fastapi import HTTPException
from src.core.utils import handle_exceptions
from src.core.utils.validators import validate_custom_filter_data
from src.integrations.logging_client import LoggingClient
from src.core.logic_manager.handlers.utils import get_template
from src.core.logic_manager.base import Block
import asyncio

logging_client = LoggingClient(service_name="bot_constructor")

class CustomFilterHandler:
    """
    Handler for processing custom filter blocks.
    """

    def __init__(self):
        pass

    @handle_exceptions
    async def handle_custom_filter(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        bot_logic: Dict[str, Any],
        user_message: str,
    ) -> Optional[int]:
        """Handles custom filter block."""
        content = block.get("content", {})
        logging_client.info(
            f"Handling custom filter block with id: {block.get('id')} for chat_id: {chat_id}"
        )
        validate_custom_filter_data(content)
        filter_expression_template = content.get("filter")
        if filter_expression_template:
            filter_expression = get_template(filter_expression_template).render(
                variables=variables
            )
            try:
                if eval(filter_expression, {}, variables):
                    logging_client.info(f"Custom filter passed: {filter_expression}")
                    from src.core.logic_manager import LogicManager
                    logic_manager = LogicManager()
                    next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                    if next_blocks:
                      return next_blocks[0].get("id")
                else:
                    logging_client.info(f"Custom filter failed: {filter_expression}")
                    return None
            except Exception as e:
                logging_client.error(f"Custom filter failed with error: {e}")
                raise
        else:
            logging_client.warning("Custom filter was not defined")
            return None

        return None