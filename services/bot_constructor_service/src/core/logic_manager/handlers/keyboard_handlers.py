from typing import Any, Dict

from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.integrations.telegram import TelegramClient
from src.core.logic_manager.base import Block

logging_client = LoggingClient(service_name="bot_constructor")


async def _handle_keyboard_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles keyboard block."""
    logging_client.info(f"Handling keyboard block for chat_id: {chat_id}")
    keyboard_type = content.get("keyboard_type")
    buttons = content.get("buttons")
    if keyboard_type and buttons:
        rendered_buttons = []
        for row in buttons:
            rendered_row = []
            for button in row:
                if isinstance(button, dict) and button.get("text"):
                    rendered_text = get_template(button["text"]).render(variables)
                    rendered_row.append({
                        "text": rendered_text,
                        "callback_data": button.get("callback_data")
                    })
                else:
                    rendered_row.append(button)
            rendered_buttons.append(rendered_row)

        if keyboard_type == "reply":
            await TelegramClient().send_message(
                chat_id,
                "Please select option:",
                reply_markup=rendered_buttons
            )
        elif keyboard_type == "inline":
            await TelegramClient().send_message(
                chat_id,
                "Please select option:",
                inline_keyboard=rendered_buttons
            )
        else:
            logging_client.warning(f"Unsupported keyboard type: {keyboard_type}")

async def _handle_callback_block(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles callback block."""
    logging_client.info(f"Handling callback block for chat_id: {chat_id}")
    callback_data_template = content.get("callback_data")
    if not callback_data_template:
        logging_client.warning("Callback data was not defined in callback block")
        return

    callback_data = get_template(callback_data_template).render(variables)
    logging_client.info(
        f"Callback data: {callback_data}. User message: {user_message}"
    )
    if callback_data in user_message:
        logging_client.info(
            f"Callback matches with user message: {user_message}"
        )
        # Do nothing, callback is already handled
        return
    else:
        logging_client.info(
            f"Callback does not match with user message"
        )
        return