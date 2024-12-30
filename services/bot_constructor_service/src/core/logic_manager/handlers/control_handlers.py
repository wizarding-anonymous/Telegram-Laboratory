from typing import Any, Dict

from fastapi import HTTPException
from src.core.utils.validators import validate_variable_data, validate_timer_data, validate_rate_limiting_data, validate_custom_filter_data
from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.integrations.redis_client import redis_client
from src.core.logic_manager.base import Block
import asyncio

logging_client = LoggingClient(service_name="bot_constructor")


async def handle_variable_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles variable block."""
    logging_client.info(f"Handling variable block {block.id}")
    validate_variable_data(content)
    action = content.get('action')
    variable_name = content.get('name')
    if not action or not variable_name:
        logging_client.warning("Variable action and name were not provided")
        return

    if action == "define":
        value = content.get("value")
        if value:
            rendered_value = get_template(str(value)).render(variables)
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
            rendered_value = get_template(str(value)).render(variables)
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
            rendered_value = get_template(str(value)).render(variables)
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

async def handle_try_catch_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles try-catch block."""
    logging_client.info(
        f"Handling try-catch block: {block.id} for chat_id: {chat_id}"
    )
    from src.core.logic_manager.base import Block
    from src.core.logic_manager import LogicManager
    logic_manager = LogicManager()
    try:
        next_blocks = await logic_manager._get_next_blocks(block.id, bot_logic)
        if next_blocks:
            for next_block in next_blocks:
                await logic_manager._process_block(next_block, chat_id, user_message, bot_logic, variables)
    except Exception as e:
        logging_client.error(f"An exception occurred in try block: {e}")
        catch_block_id = content.get("catch_block_id")
        if catch_block_id:
             from src.db.repositories import BlockRepository
             block_repository = BlockRepository()
             catch_block = await block_repository.get_by_id(catch_block_id)
             if catch_block:
                 await logic_manager._process_block(Block(**catch_block.model_dump()), chat_id, user_message, bot_logic, variables)
             else:
                  logging_client.warning(f"Catch block with id: {catch_block_id} was not found")
        else:
            logging_client.warning("Catch block was not defined in try block")
            return


async def handle_raise_error_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles raise error block."""
    logging_client.info(f"Handling raise error block")
    message_template = content.get("message")
    if message_template:
        message = get_template(message_template).render(variables)
        logging_client.error(f"Error raised by bot: {message}")
        raise HTTPException(status_code=400, detail=message)
    else:
        logging_client.warning("Error message was not provided")


async def handle_handle_exception_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles handle exception block."""
    logging_client.info(f"Handling handle exception block")
    exception_block_id = content.get("exception_block_id")
    if exception_block_id:
        from src.core.logic_manager.base import Block
        from src.db.repositories import BlockRepository
        block_repository = BlockRepository()
        exception_block = await block_repository.get_by_id(exception_block_id)
        if exception_block:
            from src.core.logic_manager import LogicManager
            logic_manager = LogicManager()
            await logic_manager._process_block(Block(**exception_block.model_dump()), chat_id, user_message, bot_logic, variables)
        else:
            logging_client.warning(f"Exception block with id: {exception_block_id} was not found")
    else:
        logging_client.warning("Exception block was not defined")
        return

async def handle_log_message_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles log message block."""
    logging_client.info(f"Handling log message block for chat_id: {chat_id}")
    message_template = content.get("message")
    level = content.get("level", "INFO").upper()

    if message_template:
        message = get_template(message_template).render(variables)
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


async def handle_timer_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles timer block."""
    logging_client.info(f"Handling timer block for chat_id: {chat_id}")
    validate_timer_data(content)
    delay_template = content.get("delay")
    if delay_template:
        try:
            delay = int(get_template(str(delay_template)).render(variables))
            if delay > 0:
                logging_client.info(f"Waiting for {delay} seconds")
                await asyncio.sleep(delay)
                from src.core.logic_manager import LogicManager
                logic_manager = LogicManager()
                next_blocks = await logic_manager._get_next_blocks(block.id, bot_logic)
                if next_blocks:
                    await asyncio.gather(
                        *[
                            logic_manager._process_block(
                                next_block,
                                chat_id,
                                user_message,
                                bot_logic,
                                variables,
                            )
                            for next_block in next_blocks
                        ]
                    )
            else:
                logging_client.warning("Delay is less or equals to 0")
        except ValueError as e:
            logging_client.error(f"Can't convert delay to int, error: {e}")
    else:
        logging_client.warning("Timer delay was not defined")
        return


async def handle_custom_filter_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles custom filter block."""
    logging_client.info(f"Handling custom filter block for chat_id: {chat_id}")
    validate_custom_filter_data(content)
    filter_expression_template = content.get("filter")
    if filter_expression_template:
        filter_expression = get_template(filter_expression_template).render(variables)
        try:
            if eval(filter_expression, {}, variables):
                logging_client.info(f"Custom filter passed: {filter_expression}")
                from src.core.logic_manager import LogicManager
                logic_manager = LogicManager()
                next_blocks = await logic_manager._get_next_blocks(block.id, bot_logic)
                if next_blocks:
                    await asyncio.gather(
                        *[
                            logic_manager._process_block(
                                next_block,
                                chat_id,
                                user_message,
                                bot_logic,
                                variables,
                            )
                            for next_block in next_blocks
                        ]
                    )
            else:
                logging_client.info(f"Custom filter failed: {filter_expression}")
                return
        except Exception as e:
            logging_client.error(f"Custom filter failed with error: {e}")
            return
    else:
        logging_client.warning("Custom filter was not defined")

async def handle_rate_limiting_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles rate limiting block."""
    logging_client.info(f"Handling rate limiting block for chat_id: {chat_id}")
    validate_rate_limiting_data(content)
    limit_template = content.get("limit")
    interval_template = content.get("interval")
    if limit_template and interval_template:
        try:
            limit = int(get_template(str(limit_template)).render(variables))
            interval = int(get_template(str(interval_template)).render(variables))
            cache_key = f"rate_limit:{chat_id}:{block.id}"
            current_count = await redis_client.get(cache_key)
            current_count = int(current_count) if current_count else 0

            if current_count < limit:
                await redis_client.setex(cache_key, interval, current_count + 1)
                logging_client.info(
                    f"Rate limit passed, current count: {current_count + 1}"
                )
                from src.core.logic_manager import LogicManager
                logic_manager = LogicManager()
                next_blocks = await logic_manager._get_next_blocks(block.id, bot_logic)
                if next_blocks:
                    await asyncio.gather(
                        *[
                            logic_manager._process_block(
                                next_block,
                                chat_id,
                                user_message,
                                bot_logic,
                                variables,
                            )
                            for next_block in next_blocks
                        ]
                    )
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
        return