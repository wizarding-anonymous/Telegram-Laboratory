# src/core/logic_manager/handlers/message_handlers.py
from typing import Any, Dict, Optional
from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.integrations.telegram import TelegramClient
from src.core.logic_manager.base import Block

logging_client = LoggingClient(service_name="bot_constructor")


async def _handle_text_message(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles a text message block."""
    logging_client.info(f"Handling text message for chat_id: {chat_id}")
    text_template = content.get("text")
    if text_template:
        text = get_template(text_template).render(variables)
        logging_client.info(
            f"User sent: {user_message}. Block text: {text}"
        )
        if text in user_message:
            logging_client.info("User message matches with content")
            # Do nothing, message is already handled
            return
        else:
            logging_client.info("User message does not match with content")

async def _handle_send_text(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles sending a text message block."""
    logging_client.info(f"Handling send text block for chat_id: {chat_id}")
    text_template = content.get("text")
    if text_template:
        text = get_template(text_template).render(variables)
        logging_client.info(
            f"Sending text message: {text} to chat_id: {chat_id}"
        )
        await TelegramClient().send_message(chat_id, text)

async def _handle_media_message(
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles various media message blocks."""
        media_type = content.get("type")  # e.g., 'photo', 'video', etc.
        if not media_type:
            logging_client.warning("Media type not defined in media message block")
            return

        caption_template = content.get("caption", "")
        if caption_template:
            caption = get_template(caption_template).render(variables)
            logging_client.info(
                f"User sent: {user_message}. Block caption: {caption}"
            )
        # Дополнительная логика обработки медиа, если требуется

async def _handle_location_message(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles a location message block."""
    logging_client.info(f"Handling location message for chat_id: {chat_id}")
    latitude_template = content.get("latitude")
    longitude_template = content.get("longitude")
    if latitude_template and longitude_template:
        latitude = get_template(str(latitude_template)).render(variables)
        longitude = get_template(str(longitude_template)).render(variables)
        logging_client.info(
            f"Location received latitude: {latitude}, longitude: {longitude}"
        )

async def _handle_contact_message(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles a contact message block."""
    logging_client.info(f"Handling contact message for chat_id: {chat_id}")
    phone_number_template = content.get("phone_number")
    if phone_number_template:
        phone_number = get_template(phone_number_template).render(variables)
        logging_client.info(
            f"User sent contact with number: {phone_number}"
        )

async def _handle_venue_message(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles a venue message block."""
    logging_client.info(f"Handling venue message for chat_id: {chat_id}")
    address_template = content.get("address")
    if address_template:
        address = get_template(address_template).render(variables)
        logging_client.info(
            f"User sent venue with address: {address}"
        )

async def _handle_game_message(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles a game message block."""
    logging_client.info(f"Handling game message for chat_id: {chat_id}")
    game_short_name_template = content.get("game_short_name")
    if game_short_name_template:
        game_short_name = get_template(game_short_name_template).render(variables)
        logging_client.info(
            f"User sent game with short name: {game_short_name}"
        )

async def _handle_poll_message(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles a poll message block."""
    logging_client.info(f"Handling poll message for chat_id: {chat_id}")
    question_template = content.get("question")
    if question_template:
        question = get_template(question_template).render(variables)
        options = content.get("options", [])
        parsed_options = [
            get_template(option).render(variables) for option in options
        ]
        logging_client.info(
            f"Sending poll with question: {question} and options: {parsed_options} to chat_id: {chat_id}"
        )
        await TelegramClient().send_poll(
            chat_id, question, parsed_options
        )

async def _handle_send_media(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles sending various media types."""
    media_type = content.get("media_type", "photo")
    media_url_template = content.get(f"{media_type}_url")
    caption_template = content.get("caption", "")
    if media_url_template:
        media_url = get_template(media_url_template).render(variables)
        caption = get_template(caption_template).render(variables) if caption_template else None
        logging_client.info(
            f"Sending {media_type} with url: {media_url} to chat_id: {chat_id}"
        )
        await TelegramClient().send_media(chat_id, media_url, caption, media_type)

async def _handle_send_location(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles sending a location message block."""
    logging_client.info(f"Handling send location block for chat_id: {chat_id}")
    latitude_template = content.get("latitude")
    longitude_template = content.get("longitude")
    if latitude_template and longitude_template:
        latitude = get_template(str(latitude_template)).render(variables)
        longitude = get_template(str(longitude_template)).render(variables)
        logging_client.info(
            f"Sending location latitude: {latitude} and longitude: {longitude} to chat_id: {chat_id}"
        )
        await TelegramClient().send_location(
            chat_id, float(latitude), float(longitude)
        )

async def _handle_send_contact(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles sending a contact message block."""
    logging_client.info(f"Handling send contact block for chat_id: {chat_id}")
    phone_number_template = content.get("phone_number")
    first_name_template = content.get("first_name", "")
    last_name_template = content.get("last_name", "")
    if phone_number_template:
        phone_number = get_template(phone_number_template).render(variables)
        first_name = get_template(first_name_template).render(variables) if first_name_template else ""
        last_name = get_template(last_name_template).render(variables) if last_name_template else ""
        logging_client.info(
            f"Sending contact with number: {phone_number} to chat_id: {chat_id}"
        )
        await TelegramClient().send_contact(
            chat_id, phone_number, first_name, last_name=last_name
        )

async def _handle_send_venue(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles sending a venue message block."""
    logging_client.info(f"Handling send venue block for chat_id: {chat_id}")
    address_template = content.get("address")
    latitude_template = content.get("latitude", "0")
    longitude_template = content.get("longitude", "0")
    title_template = content.get("title", "")
    if address_template and latitude_template and longitude_template:
        address = get_template(address_template).render(variables)
        latitude = get_template(str(latitude_template)).render(variables)
        longitude = get_template(str(longitude_template)).render(variables)
        title = get_template(title_template).render(variables) if title_template else ""
        logging_client.info(
            f"Sending venue with address: {address}, latitude: {latitude} and longitude: {longitude} to chat_id: {chat_id}"
        )
        await TelegramClient().send_venue(
            chat_id, float(latitude), float(longitude), title, address
        )

async def _handle_send_game(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
     block: Block,
) -> None:
    """Handles sending a game message block."""
    logging_client.info(f"Handling send game block for chat_id: {chat_id}")
    game_short_name_template = content.get("game_short_name")
    if game_short_name_template:
        game_short_name = get_template(game_short_name_template).render(variables)
        logging_client.info(
            f"Sending game with short name: {game_short_name} to chat_id: {chat_id}"
        )
        await TelegramClient().send_game(chat_id, game_short_name)

async def _handle_send_poll(
    content: Dict[str, Any],
    chat_id: int,
    user_message: str,
    bot_logic: Dict[str, Any],
    variables: Dict[str, Any],
    block: Block,
) -> None:
    """Handles sending a poll message block."""
    logging_client.info(f"Handling send poll block for chat_id: {chat_id}")
    question_template = content.get("question")
    options = content.get("options", [])
    if question_template and options:
        question = get_template(question_template).render(variables)
        parsed_options = [
            get_template(option).render(variables) for option in options
        ]
        logging_client.info(
            f"Sending poll with question: {question} and options: {parsed_options} to chat_id: {chat_id}"
        )
        await TelegramClient().send_poll(
            chat_id, question, parsed_options
        )