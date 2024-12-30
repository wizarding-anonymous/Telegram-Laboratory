from typing import Any, Dict, List, Optional

from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.integrations.telegram.client import TelegramClient
from src.core.logic_manager.base import Block
from src.core.utils import handle_exceptions, validate_keyboard_data, validate_callback_data

logging_client = LoggingClient(service_name="bot_constructor")


class KeyboardHandler:
    """
    Handler for processing keyboard blocks.
    """

    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_keyboard(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles keyboard block."""
        logging_client.info(f"Handling keyboard block for chat_id: {chat_id}")
        validate_keyboard_data(content)
        keyboard_type = content.get("type")
        buttons = content.get("buttons")
        if keyboard_type and buttons:
            rendered_buttons = []
            for button in buttons:
              if isinstance(button, dict):
                  rendered_button = {}
                  if button.get("text"):
                    rendered_button["text"] = get_template(button["text"]).render(variables=variables)
                  if button.get("callback_data"):
                      rendered_button["callback_data"] = button.get("callback_data")
                  if button.get("url"):
                      rendered_button["url"] = button.get("url")

                  rendered_buttons.append(rendered_button)
              else:
                  rendered_buttons.append(button)

            if keyboard_type == "reply":
                await self.telegram_client.send_message(
                    chat_id,
                    "Please select option:",
                    reply_markup=rendered_buttons,
                )
            elif keyboard_type == "inline":
                await self.telegram_client.send_message(
                    chat_id,
                    "Please select option:",
                    inline_keyboard=rendered_buttons,
                )
            else:
                logging_client.warning(f"Unsupported keyboard type: {keyboard_type}")

    @handle_exceptions
    async def handle_callback_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> str:
        """Handles callback block."""
        logging_client.info(f"Handling callback block for chat_id: {chat_id}")
        validate_callback_data(content)
        callback_data_template = content.get("data")
        if not callback_data_template:
            logging_client.warning("Callback data was not defined in callback block")
            return ""

        callback_data = get_template(callback_data_template).render(variables=variables)
        logging_client.info(
            f"Callback data: {callback_data}. User message: {user_message}"
        )
        return callback_data