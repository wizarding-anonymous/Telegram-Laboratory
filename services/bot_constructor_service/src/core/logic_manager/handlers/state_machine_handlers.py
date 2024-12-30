from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.redis_client import redis_client
import json
from src.core.logic_manager.handlers.utils import get_template
from src.db.repositories import BlockRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.config import settings
from src.integrations.logging_client import LoggingClient
from src.core.logic_manager.base import Block


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


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
        bot_logic: Dict[str, Any],
        user_message: str
    ) -> Optional[int]:
        """
        Handles the state machine logic.

        Args:
            block (dict): The state machine block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
            bot_logic (dict): Bot logic.
            user_message (str): Current user message.

        Returns:
            Optional[int]: The ID of the next block to execute, or None if no transition.
        """
        logging_client.info(f"Handling state machine block: {block.get('id')} for chat_id: {chat_id}")
        content = block.get("content", {})
        initial_state = content.get("initial_state")
        transitions = content.get("transitions", [])

        user_key = f"state_user:{chat_id}:{block.get('id')}"
        current_state = await redis_client.get(user_key)

        if current_state is None:
            current_state = initial_state
            if current_state:
              current_state = get_template(current_state).render(variables=variables)
              await redis_client.set(user_key, current_state)
            else:
                 logging_client.warning("Initial state for state machine was not defined")
                 return None
           
        for transition in transitions:
            from_state = transition.get("from_state")
            if from_state:
                from_state = get_template(from_state).render(variables=variables)
                if from_state != current_state:
                     continue
            else:
                 logging_client.warning("From state was not defined in state machine")
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
                    logging_client.debug("Last user message was not found in redis")
                    continue
                last_user_message = json.loads(last_user_message).get("text")
                if last_user_message == condition_value:
                   if to_state:
                        to_state = get_template(to_state).render(variables=variables)
                        await redis_client.set(user_key, to_state)
                   logging_client.info(
                      f"State transition triggered by message, to state: {to_state}, next block id: {next_block_id}"
                   )
                   return next_block_id

            elif condition_type == "variable_equals":
                 if variable_value:
                     variable_value = get_template(str(variable_value)).render(variables=variables)
                     if variables.get(condition_value) == variable_value:
                          if to_state:
                              to_state = get_template(to_state).render(variables=variables)
                              await redis_client.set(user_key, to_state)
                          logging_client.info(
                            f"State transition triggered by variable, to state: {to_state}, next block id: {next_block_id}"
                         )
                          return next_block_id
                 else:
                     logging_client.warning(
                         "Variable for condition was not defined"
                     )
                     continue

            elif condition_type == "always":
                if to_state:
                  to_state = get_template(to_state).render(variables=variables)
                  await redis_client.set(user_key, to_state)
                logging_client.info(
                    f"State transition triggered by 'always' condition, to state: {to_state}, next block id: {next_block_id}"
                )
                return next_block_id
        logging_client.warning(f"No transitions matched for state: {current_state} and message: {user_message}")
        return None  # If no transitions match, return None

    @handle_exceptions
    async def save_user_message(self, message: Dict[str, Any], chat_id: int) -> None:
        """Saves user message to redis for state machine condition checks

        Args:
            message (dict): The telegram message.
            chat_id (int): Telegram chat ID where the interaction is happening.
        """
        logging_client.info(f"Saving last user message for chat_id: {chat_id}")
        last_user_message_key = f"last_user_message:{chat_id}"
        message_json = json.dumps(message)
        await redis_client.set(last_user_message_key, message_json)
        logging_client.debug(f"Last user message was saved: {message_json}")

    @handle_exceptions
    async def get_current_state(self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]) -> Optional[str]:
        """
        Get current state for specific user
         Args:
            block (dict): The state machine block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
        Returns:
            Optional[str]: Current state for user
        """
        logging_client.info(f"Getting current state for chat_id: {chat_id} and block_id: {block.get('id')}")
        user_key = f"state_user:{chat_id}:{block.get('id')}"
        current_state = await redis_client.get(user_key)
        if current_state:
            logging_client.debug(f"Current state was found in redis: {current_state}")
        else:
            logging_client.debug(f"Current state was not found in redis")
        return current_state