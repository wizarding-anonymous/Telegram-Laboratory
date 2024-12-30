from typing import Any, Dict, Optional

from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.db.repositories import BlockRepository
from src.integrations.auth_service import AuthService
from src.core.logic_manager.base import Block
import asyncio
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)
auth_service = AuthService()
block_repository = BlockRepository()


class FlowHandler:
    """
    Handler for processing flow control blocks.
    """

    def __init__(self):
        pass

    @handle_exceptions
    async def handle_if_condition(
        self,
        block: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
    ) -> Optional[int]:
        """Handles if condition block."""
        logging_client.info(
            f"Handling if condition block: {block.get('id')} for chat_id: {chat_id}"
        )
        content = block.get("content", {})
        condition_template = content.get("condition")
        if not condition_template:
             logging_client.warning(f"Condition was not provided for the if block: {block.get('id')}")
             return None
        try:
            condition = get_template(str(condition_template)).render(variables=variables)
            if eval(condition, {}, variables):
                logging_client.info(f"If condition passed, condition: {condition}")
                from src.core.logic_manager import LogicManager
                logic_manager = LogicManager()
                next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                if next_blocks:
                  return next_blocks[0].get("id")
                return None
            else:
                logging_client.info(f"If condition failed, condition: {condition}")
                else_block_id = content.get("else_block_id")
                return else_block_id
        except Exception as e:
            logging_client.error(f"If condition failed with error: {e}")
            return None

    @handle_exceptions
    async def handle_loop_block(
        self,
        block: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
    ) -> Optional[int]:
        """Handles loop block."""
        logging_client.info(
            f"Handling loop block: {block.get('id')} for chat_id: {chat_id}"
        )
        content = block.get("content", {})
        loop_type = content.get("loop_type")
        loop_count = content.get("count", 0)
        if loop_type == "for":
            try:
                count = int(get_template(str(loop_count)).render(variables=variables))
                if count > 0:
                    for i in range(count):
                        logging_client.info(
                            f"Executing loop iteration {i + 1} for block: {block.get('id')}"
                        )
                        loop_variables = {**variables, "loop_index": i}
                        from src.core.logic_manager import LogicManager
                        logic_manager = LogicManager()
                        next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                        if next_blocks:
                            for next_block in next_blocks:
                                await logic_manager._process_block(
                                    Block(**next_block.model_dump()),
                                    chat_id,
                                    user_message,
                                    bot_logic,
                                    loop_variables,
                                )
                    next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                    if next_blocks:
                        return next_blocks[0].get("id")

                else:
                    logging_client.warning("Loop count is less or equals to 0")
            except ValueError as e:
                logging_client.error(f"Can't convert {loop_count} to int, error: {e}")
        elif loop_type == "while":
            condition_template = content.get("condition")
            if condition_template:
                condition = get_template(condition_template).render(variables=variables)
                while eval(condition, {}, variables):
                    logging_client.info(
                        f"Executing while loop for block: {block.get('id')} and condition {condition}"
                    )
                    from src.core.logic_manager import LogicManager
                    logic_manager = LogicManager()
                    next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                    if next_blocks:
                        for next_block in next_blocks:
                            await logic_manager._process_block(
                                    Block(**next_block.model_dump()),
                                    chat_id,
                                    user_message,
                                    bot_logic,
                                    variables,
                            )
                    condition = get_template(condition_template).render(variables=variables)
                next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                if next_blocks:
                   return next_blocks[0].get("id")
            else:
                logging_client.warning(f"While loop requires condition in {block.get('id')}")
        return None
   
    @handle_exceptions
    async def handle_switch_case(self,
            block: Dict[str, Any],
            chat_id: int,
            user_message: str,
            bot_logic: Dict[str, Any],
            variables: Dict[str, Any],
        ) -> Optional[int]:
        """Handles switch case block."""
        logging_client.info(f"Handling switch case block {block.get('id')} for chat_id: {chat_id}")
        content = block.get("content", {})
        switch_value_template = content.get("switch_value")
        cases = content.get("cases", [])
        if not switch_value_template:
             logging_client.warning("Switch value was not provided")
             return None

        switch_value = get_template(str(switch_value_template)).render(variables=variables)
        for case in cases:
             case_value_template = case.get("case_value")
             target_block_id = case.get("target_block_id")
             if case_value_template and target_block_id:
                 case_value = get_template(case_value_template).render(variables)
                 if case_value == switch_value:
                   logging_client.info(f"Switch case found case value: {case_value} and switch value: {switch_value}. Executing target_block_id: {target_block_id}")
                   return target_block_id
             else:
               logging_client.warning(f"case value or target_block_id was not provided")
        logging_client.info(f"Switch case not found for value: {switch_value}")
        return None