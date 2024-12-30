from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.redis_client import redis_client
import json
from src.core.logic_manager.handlers.utils import get_template
from src.config import settings
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class UserHandler:
    """
    Handler for processing user-related blocks.
    """

    def __init__(self):
        pass

    @handle_exceptions
    async def handle_save_user_data(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Saves user data to Redis.

        Args:
            block (dict): The save user data block details from database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        content = block.get("content", {})
        logging_client.info(f"Handling save user data block {block.get('id')} for chat_id: {chat_id}")
        data_to_save = content.get("data", {})
        user_data_key = f"user_data:{chat_id}"

        if isinstance(data_to_save, dict):
             rendered_data_to_save = {}
             for key, value in data_to_save.items():
                rendered_value = get_template(str(value)).render(variables=variables)
                rendered_data_to_save[key] = rendered_value
             
             existing_data_json = await redis_client.get(user_data_key)
             existing_data = (
                json.loads(existing_data_json) if existing_data_json else {}
            )
             updated_data = {**existing_data, **rendered_data_to_save}
             await redis_client.set(user_data_key, json.dumps(updated_data))
             logging_client.info(f"User data saved for chat_id: {chat_id}, data: {updated_data}")

        elif data_to_save:
            template = get_template(str(data_to_save))
            rendered_data = template.render(variables=variables)
            await redis_client.set(user_data_key, json.dumps(rendered_data))
            logging_client.info(f"User data saved for chat_id: {chat_id}, data: {rendered_data}")
        
    @handle_exceptions
    async def handle_retrieve_user_data(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Retrieves user data from Redis and sets it into variables.

        Args:
            block (dict): The retrieve user data block details from database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.

        Returns:
            Optional[Any]: The retrieved data, or None if not found.
        """
        logging_client.info(f"Handling retrieve user data block {block.get('id')} for chat_id: {chat_id}")
        user_data_key = f"user_data:{chat_id}"
        data_key_to_retrieve = block.get("content", {}).get("key")

        user_data_json = await redis_client.get(user_data_key)
        if not user_data_json:
            logging_client.info(f"User data not found for chat_id: {chat_id}")
            return None

        user_data = json.loads(user_data_json)
        if data_key_to_retrieve:
            retrieved_data = user_data.get(data_key_to_retrieve)
            logging_client.info(f"User data retrieved successfully for key '{data_key_to_retrieve}' and chat_id: {chat_id}")
            return retrieved_data
        logging_client.info(f"All user data retrieved successfully for chat_id: {chat_id}")
        return user_data

    @handle_exceptions
    async def handle_clear_user_data(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Clears user data from Redis.

        Args:
            block (dict): The clear user data block details from database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        logging_client.info(f"Handling clear user data block for chat_id: {chat_id}")
        user_data_key = f"user_data:{chat_id}"
        await redis_client.delete(user_data_key)
        logging_client.info(f"User data cleared successfully for chat_id: {chat_id}")

    @handle_exceptions
    async def handle_manage_session(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Manages user sessions (e.g., setting session variables).

        Args:
            block (dict): The manage session block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        content = block.get("content", {})
        logging_client.info(f"Handling manage session block {block.get('id')} for chat_id: {chat_id}")
        session_data = content.get("session_data")
        user_session_key = f"session:{chat_id}"
        if session_data:
            if isinstance(session_data, dict):
                rendered_session_data = {}
                for key, value in session_data.items():
                   rendered_value = get_template(str(value)).render(variables=variables)
                   rendered_session_data[key] = rendered_value

                existing_session_json = await redis_client.get(user_session_key)
                existing_session = (
                    json.loads(existing_session_json) if existing_session_json else {}
                )
                updated_session = {**existing_session, **rendered_session_data}
                await redis_client.set(user_session_key, json.dumps(updated_session))
                logging_client.info(f"Session data updated for chat_id: {chat_id}, data: {updated_session}")
            else:
                template = get_template(str(session_data))
                rendered_session_data = template.render(variables=variables)
                await redis_client.set(user_session_key, json.dumps(rendered_session_data))
                logging_client.info(f"Session data updated for chat_id: {chat_id}, data: {rendered_session_data}")