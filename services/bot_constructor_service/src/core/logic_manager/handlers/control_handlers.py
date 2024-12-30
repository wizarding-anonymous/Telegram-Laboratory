from typing import Any, Dict, Optional
from fastapi import HTTPException
from src.core.utils import handle_exceptions
from src.core.utils.validators import (
    validate_variable_data,
    validate_timer_data,
    validate_rate_limiting_data,
    validate_custom_filter_data,
)
from src.core.logic_manager.handlers.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.integrations.redis_client import redis_client
from src.config import settings
import asyncio


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class ControlHandler:
    """
    Handler for processing control flow and logic blocks.
    """

    def __init__(self):
        pass

    @handle_exceptions
    async def handle_variable_block(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
    ) -> None:
        """Handles variable block."""
        content = block.get("content", {})
        logging_client.info(f"Handling variable block {block.get('id')}")
        validate_variable_data(content)
        action = content.get("name")
        variable_name = content.get("name")
        if not action or not variable_name:
            logging_client.warning("Variable action and name were not provided")
            return

        if action == "define":
            value = content.get("value")
            if value:
                rendered_value = get_template(str(value)).render(variables=variables)
                variables[variable_name] = rendered_value
                logging_client.info(
                    f"Defining variable: {variable_name} with value: {rendered_value}"
                )
            else:
                variables[variable_name] = None
                logging_client.info(
                    f"Defining variable: {variable_name} with value: None"
                )

        elif action == "assign":
            value = content.get("value")
            if value:
                rendered_value = get_template(str(value)).render(variables=variables)
                variables[variable_name] = rendered_value
                logging_client.info(
                    f"Assigning value: {rendered_value} to variable: {variable_name}"
                )
            else:
                logging_client.warning(
                    f"Value for assignment of {variable_name} was not provided"
                )
                return
        elif action == "retrieve":
            retrieved_value = variables.get(variable_name)
            logging_client.info(
                f"Retrieving value of variable: {variable_name} and value is {retrieved_value}"
            )
        elif action == "update":
            value = content.get("value")
            if value:
                rendered_value = get_template(str(value)).render(variables=variables)
                variables[variable_name] = rendered_value
                logging_client.info(
                    f"Updating variable: {variable_name} with value: {rendered_value}"
                )
            else:
                logging_client.warning(
                    f"Value for update of {variable_name} was not provided"
                )
                return
        else:
            logging_client.warning(f"Unsupported variable action: {action}")

    @handle_exceptions
    async def handle_if_condition(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        bot_logic: Dict[str, Any],
        current_block_id: int,
        user_message: str,
    ) -> Optional[int]:
        """Handles the if condition block."""
        logging_client.info(
            f"Handling if condition block {block.get('id')} for chat_id: {chat_id}"
        )
        condition_template = block.get("content", {}).get("condition")
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
                else_block_id = block.get("content", {}).get("else_block_id")
                return else_block_id
        except Exception as e:
            logging_client.error(f"If condition failed with error: {e}")
            return None

    @handle_exceptions
    async def handle_wait_for_message(self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]) -> None:
         """Handles wait for message block."""
         logging_client.info(f"Handling wait for message block for chat_id: {chat_id}")
         # This block just waits for the user message it doesn't do any processing
         return None

    @handle_exceptions
    async def handle_try_catch_block(
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
    async def handle_raise_error_block(
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
    async def handle_handle_exception_block(
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

    @handle_exceptions
    async def handle_log_message_block(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
         user_message: str,
           bot_logic: Dict[str, Any],
    ) -> None:
        """Handles log message block."""
        content = block.get("content", {})
        logging_client.info(f"Handling log message block {block.get('id')} for chat_id: {chat_id}")
        message_template = content.get("message")
        level = content.get("level", "INFO").upper()

        if message_template:
            message = get_template(message_template).render(variables=variables)
            if level == "INFO":
                logging_client.info(f"Log message: {message}")
            elif level == "DEBUG":
                logging_client.debug(f"Log message: {message}")
            elif level == "WARNING":
                logging_client.warning(f"Log message: {message}")
            elif level == "ERROR":
                logging_client.error(f"Log message: {message}")
            elif level == "CRITICAL":
                logging_client.critical(f"Log message: {message}")
            else:
                logging_client.warning(f"Unsupported log level: {level}")
                return
        else:
            logging_client.warning("Log message or level was not provided")

    @handle_exceptions
    async def handle_timer_block(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
         bot_logic: Dict[str, Any],
        user_message: str,
    ) -> Optional[int]:
        """Handles timer block."""
        content = block.get("content", {})
        logging_client.info(f"Handling timer block {block.get('id')} for chat_id: {chat_id}")
        validate_timer_data(content)
        delay_template = content.get("delay")
        if delay_template:
            try:
                delay = int(get_template(str(delay_template)).render(variables=variables))
                if delay > 0:
                    logging_client.info(f"Waiting for {delay} seconds")
                    await asyncio.sleep(delay)
                    from src.core.logic_manager import LogicManager
                    logic_manager = LogicManager()
                    next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                    if next_blocks:
                        return next_blocks[0].get("id")
                    return None
                else:
                    logging_client.warning("Delay is less or equals to 0")
            except ValueError as e:
                logging_client.error(f"Can't convert delay to int, error: {e}")
        else:
            logging_client.warning("Timer delay was not defined")
        return None


    @handle_exceptions
    async def handle_custom_filter_block(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        bot_logic: Dict[str, Any],
        user_message: str
    ) -> Optional[int]:
        """Handles custom filter block."""
        content = block.get("content", {})
        logging_client.info(f"Handling custom filter block {block.get('id')} for chat_id: {chat_id}")
        validate_custom_filter_data(content)
        filter_expression_template = content.get("filter")
        if filter_expression_template:
            filter_expression = get_template(filter_expression_template).render(variables=variables)
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
                return None
        else:
            logging_client.warning("Custom filter was not defined")
        return None

    @handle_exceptions
    async def handle_rate_limiting_block(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        bot_logic: Dict[str, Any],
        user_message: str
    ) -> Optional[int]:
        """Handles rate limiting block."""
        content = block.get("content", {})
        logging_client.info(f"Handling rate limiting block {block.get('id')} for chat_id: {chat_id}")
        validate_rate_limiting_data(content)
        limit_template = content.get("limit")
        interval_template = content.get("interval")
        if limit_template and interval_template:
            try:
                limit = int(get_template(str(limit_template)).render(variables=variables))
                interval = int(get_template(str(interval_template)).render(variables=variables))
                cache_key = f"rate_limit:{chat_id}:{block.get('id')}"
                current_count = await redis_client.get(cache_key)
                current_count = int(current_count) if current_count else 0

                if current_count < limit:
                    await redis_client.setex(cache_key, interval, current_count + 1)
                    logging_client.info(
                        f"Rate limit passed, current count: {current_count + 1}"
                    )
                    from src.core.logic_manager import LogicManager
                    logic_manager = LogicManager()
                    next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
                    if next_blocks:
                       return next_blocks[0].get("id")
                    return None

                else:
                    logging_client.warning(
                        f"Rate limit exceeded, current count: {current_count}"
                    )
            except ValueError as e:
                logging_client.error(f"Can't convert limit or interval to int, error: {e}")
            except Exception as e:
                logging_client.error(f"Error with rate limiting, error: {e}")
        else:
            logging_client.warning("Rate limit or interval was not defined")
        return None