from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.telegram.client import TelegramClient
from src.core.utils import validate_chat_id, validate_user_id
from src.core.logic_manager.handlers.utils import get_template


class ChatHandler:
    """
    Handler for processing chat-related blocks.
    """

    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_get_chat_members(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Gets the members of a chat.

        Args:
            block (dict): The get chat members block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.

        Returns:
            List[Dict[str,Any]]: List of chat members info
        """
        validate_chat_id(chat_id)
        members = await self.telegram_client.get_chat_members(chat_id=chat_id)
        return members

    @handle_exceptions
    async def handle_ban_user(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Bans a user from a chat.

        Args:
           block (dict): The ban user block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        user_id = block.get("content", {}).get("user_id")
        validate_chat_id(chat_id)
        validate_user_id(user_id)
        await self.telegram_client.ban_chat_member(chat_id=chat_id, user_id=user_id)

    @handle_exceptions
    async def handle_unban_user(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Unbans a user from a chat.

        Args:
           block (dict): The unban user block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        user_id = block.get("content", {}).get("user_id")
        validate_chat_id(chat_id)
        validate_user_id(user_id)
        await self.telegram_client.unban_chat_member(chat_id=chat_id, user_id=user_id)

    @handle_exceptions
    async def handle_set_chat_title(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Sets the title of a chat.

        Args:
            block (dict): The set chat title block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        title = block.get("content", {}).get("title")
        validate_chat_id(chat_id)

        if title:
            template = get_template(title)
            rendered_title = template.render(variables=variables)
            await self.telegram_client.set_chat_title(
                chat_id=chat_id, title=rendered_title
            )

    @handle_exceptions
    async def handle_set_chat_description(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Sets the description of a chat.

        Args:
            block (dict): The set chat description block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        description = block.get("content", {}).get("description")
        validate_chat_id(chat_id)
        if description:
            template = get_template(description)
            rendered_description = template.render(variables=variables)
            await self.telegram_client.set_chat_description(
                chat_id=chat_id, description=rendered_description
            )

    @handle_exceptions
    async def handle_pin_message(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Pins a message in a chat.

        Args:
           block (dict): The pin message block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        message_id = block.get("content", {}).get("message_id")
        validate_chat_id(chat_id)
        if message_id:
            await self.telegram_client.pin_chat_message(
                chat_id=chat_id, message_id=message_id
            )

    @handle_exceptions
    async def handle_unpin_message(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Unpins a message in a chat.

        Args:
           block (dict): The unpin message block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        message_id = block.get("content", {}).get("message_id")
        validate_chat_id(chat_id)
        if message_id:
             await self.telegram_client.unpin_chat_message(
                 chat_id=chat_id, message_id=message_id
            )