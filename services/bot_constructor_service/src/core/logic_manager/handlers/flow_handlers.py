from typing import Any, Dict

from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.db.repositories import BlockRepository
from src.integrations.auth_service import AuthService
from src.core.logic_manager.base import Block
import asyncio

logging_client = LoggingClient(service_name="bot_constructor")
auth_service = AuthService()
block_repository = BlockRepository()

async def handle_if_condition_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles if condition block."""
    logging_client.info(
        f"Handling if condition block: {block.id} for chat_id: {chat_id}"
    )
    condition_template = content.get("condition")
    if condition_template:
        condition = get_template(condition_template).render(variables)
        if condition in user_message:
            logging_client.info(
                f"Condition: {condition} is true for user message: {user_message}. Executing connected blocks."
            )
            # Next blocks are already processed in _process_block
        else:
            logging_client.info(
                f"Condition: {condition} is false for user message: {user_message}. Skipping next blocks."
            )
            # Do nothing, skip next blocks as the condition is not met.

async def handle_loop_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles loop block."""
    logging_client.info(
        f"Handling loop block: {block.id} for chat_id: {chat_id}"
    )

    loop_type = content.get("loop_type")
    loop_count = content.get("count", 0)
    if loop_type == "for":
        try:
            count = int(get_template(str(loop_count)).render(variables))
            if count > 0:
                for i in range(count):
                    logging_client.info(
                        f"Executing loop iteration {i + 1} for block: {block.id}"
                    )
                    loop_variables = {**variables, "loop_index": i}
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
                                    loop_variables,
                                )
                                for next_block in next_blocks
                            ]
                        )
            else:
                logging_client.warning("Loop count is less or equals to 0")
        except ValueError:
            logging_client.error(
                f"Can't convert {loop_count} to int"
            )
    elif loop_type == "while":
        condition_template = content.get("condition")
        if condition_template:
            condition = get_template(condition_template).render(variables)
            while condition in user_message:
                logging_client.info(
                    f"Executing while loop for block: {block.id} and condition {condition}"
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
                condition = get_template(condition_template).render(variables)
        else:
            logging_client.warning(f"While loop requires condition in {block.id}")


async def handle_state_machine_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles state machine block."""
    logging_client.info(
        f"Handling state machine block: {block.id} for chat_id: {chat_id}"
    )
    from src.core.utils.validators import validate_state_machine_data
    validate_state_machine_data(content)
    state_template = content.get("state")
    transitions = content.get("transitions", [])
    if state_template and transitions:
        state = get_template(state_template).render(variables)
        logging_client.info(f"Current state: {state}")
        for transition in transitions:
            trigger_template = transition.get("trigger")
            target_state = transition.get("target_state")
            if trigger_template and target_state:
                trigger = get_template(trigger_template).render(variables)
                if trigger in user_message:
                    logging_client.info(
                        f"Transition triggered by: {trigger}. Moving to state: {target_state}"
                    )
                    # Здесь можно сохранить состояние для последующего использования
                    from src.core.logic_manager import LogicManager
                    logic_manager = LogicManager()
                    next_block = await block_repository.get_by_id(target_state)
                    if next_block:
                        await logic_manager._process_block(Block(**next_block.model_dump()), chat_id, user_message, bot_logic, variables)
                    else:
                        logging_client.warning(
                            f"Next block for state: {target_state} was not found"
                        )
                    return
        logging_client.warning(f"No transition was triggered from current state {state} and message {user_message}")
        return
    else:
        logging_client.warning("State and transitions were not defined")
        return