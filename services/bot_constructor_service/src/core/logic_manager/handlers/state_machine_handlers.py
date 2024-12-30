from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.redis_client import redis_client
import json
from src.core.logic_manager.handlers.utils import get_template
from src.db.repositories import BlockRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session


class StateMachineHandler:
    """
    Handler for processing state machine blocks.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.block_repository = BlockRepository(session)

    @handle_exceptions
    async def handle_state_machine(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
        current_block_id: int,
    ) -> Optional[int]:
        """
        Handles the state machine logic.

        Args:
            block (dict): The state machine block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
            current_block_id (int): ID of current block being executed

        Returns:
            Optional[int]: The ID of the next block to execute, or None if no transition.
        """
        state_machine_config = block.get("content", {})
        initial_state = state_machine_config.get("initial_state")
        transitions = state_machine_config.get("transitions", [])

        user_key = f"state_user:{chat_id}"
        current_state = await redis_client.get(user_key)

        if current_state is None:
            current_state = initial_state
            await redis_client.set(user_key, current_state)

        for transition in transitions:
            from_state = transition.get("from_state")
            if from_state != current_state:
                continue

            condition_type = transition.get("condition_type")
            condition_value = transition.get("condition_value")
            to_state = transition.get("to_state")
            next_block_id = transition.get("next_block_id")
            variable_value = transition.get("variable_value")

            if condition_type == "message_text":
                last_user_message_key = f"last_user_message:{chat_id}"
                last_user_message = await redis_client.get(last_user_message_key)
                if last_user_message is None:
                    continue
                last_user_message = json.loads(last_user_message).get("text")

                if last_user_message == condition_value:
                    await redis_client.set(user_key, to_state)
                    return next_block_id

            elif condition_type == "variable_equals":
                if variables.get(condition_value) == variable_value:
                    await redis_client.set(user_key, to_state)
                    return next_block_id

            elif condition_type == "always":
                await redis_client.set(user_key, to_state)
                return next_block_id

        return None  # If no transitions match, return None

    @handle_exceptions
    async def save_user_message(self, message: Dict[str, Any], chat_id: int) -> None:
        """Saves user message to redis for state machine condition checks

        Args:
            message (dict): The telegram message.
            chat_id (int): Telegram chat ID where the interaction is happening.
        """
        last_user_message_key = f"last_user_message:{chat_id}"
        message_json = json.dumps(message)
        await redis_client.set(last_user_message_key, message_json)

    @handle_exceptions
    async def get_current_state(self, chat_id: int) -> Optional[str]:
        """
        Get current state for specific user
         Args:
            chat_id (int): Telegram chat ID where the interaction is happening.
        Returns:
            Optional[str]: Current state for user
        """
        user_key = f"state_user:{chat_id}"
        current_state = await redis_client.get(user_key)
        return current_state