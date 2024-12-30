from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.redis_client import redis_client
import json

class UserHandler:
    """
    Handler for processing user-related blocks.
    """

    @handle_exceptions
    async def handle_save_user_data(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Saves user data to Redis.

        Args:
            block (dict): The save user data block details from database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        data_to_save = block.get("content", {}).get("data", {})
        user_data_key = f"user_data:{chat_id}"

        if isinstance(data_to_save, dict):
            
            existing_data_json = await redis_client.get(user_data_key)
            existing_data = json.loads(existing_data_json) if existing_data_json else {}
            
            
            updated_data = {**existing_data, **data_to_save}
            
            await redis_client.set(user_data_key, json.dumps(updated_data))
        
        else:
           await redis_client.set(user_data_key, json.dumps(data_to_save))
           

    @handle_exceptions
    async def handle_retrieve_user_data(self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]) -> Optional[Any]:
        """
        Retrieves user data from Redis and sets it into variables.

        Args:
            block (dict): The retrieve user data block details from database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.

        Returns:
            Optional[Any]: The retrieved data, or None if not found.
        """
        user_data_key = f"user_data:{chat_id}"
        data_key_to_retrieve = block.get("content", {}).get("key")
        
        user_data_json = await redis_client.get(user_data_key)
        if not user_data_json:
            return None

        user_data = json.loads(user_data_json)
        if data_key_to_retrieve:
           return user_data.get(data_key_to_retrieve)
        return user_data

    @handle_exceptions
    async def handle_clear_user_data(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Clears user data from Redis.

         Args:
            block (dict): The clear user data block details from database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        user_data_key = f"user_data:{chat_id}"
        await redis_client.delete(user_data_key)


    @handle_exceptions
    async def handle_manage_session(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Manages user sessions (e.g., setting session variables).

        Args:
           block (dict): The manage session block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        session_data = block.get("content", {}).get("session_data")
        user_session_key = f"session:{chat_id}"

        if isinstance(session_data, dict):
            existing_session_json = await redis_client.get(user_session_key)
            existing_session = json.loads(existing_session_json) if existing_session_json else {}
            updated_session = {**existing_session, **session_data}
            await redis_client.set(user_session_key, json.dumps(updated_session))
        else:
          await redis_client.set(user_session_key, json.dumps(session_data))