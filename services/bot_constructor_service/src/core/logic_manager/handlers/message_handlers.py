from typing import Any, Dict, Optional, List

from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.integrations.telegram.client import TelegramClient
from src.core.logic_manager.base import Block
from src.core.utils import handle_exceptions, validate_content

logging_client = LoggingClient(service_name="bot_constructor")


class TextMessageBlockHandler:
    """
    Handler for processing text message blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_text_message(
        self,
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
            text = get_template(text_template).render(variables=variables)
            logging_client.info(
                f"User sent: {user_message}. Block text: {text}"
            )
    
    @handle_exceptions
    async def handle_send_text(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles sending a text message block."""
        logging_client.info(f"Handling send text block for chat_id: {chat_id}")
        validate_content(content)
        text_template = content.get("text")
        if text_template:
            text = get_template(text_template).render(variables=variables)
            logging_client.info(
                f"Sending text message: {text} to chat_id: {chat_id}. User message was: {user_message}"
            )
            await self.telegram_client.send_message(chat_id, text)

class MediaMessageBlockHandler:
    """
    Handles media messages
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_media_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles various media message blocks."""
        logging_client.info(f"Handling media message block for chat_id: {chat_id}")
        media_type = content.get("type")  # e.g., 'photo', 'video', etc.
        if not media_type:
            logging_client.warning("Media type not defined in media message block")
            return

        caption_template = content.get("caption", "")
        if caption_template:
            caption = get_template(caption_template).render(variables=variables)
            logging_client.info(
                f"User sent: {user_message}. Block caption: {caption}"
            )

    @handle_exceptions
    async def handle_send_media(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles sending various media types."""
        logging_client.info(f"Handling send media block for chat_id: {chat_id}")
        media_type = content.get("media_type", "photo")
        media_url_template = content.get(f"{media_type}_url")
        caption_template = content.get("caption", "")
        if media_url_template:
            media_url = get_template(media_url_template).render(variables=variables)
            caption = get_template(caption_template).render(variables=variables) if caption_template else None
            logging_client.info(
                f"Sending {media_type} with url: {media_url} to chat_id: {chat_id}. User message was {user_message}"
            )
            if media_type == "photo":
                await self.telegram_client.send_photo(chat_id, media_url, caption)
            elif media_type == "video":
                await self.telegram_client.send_video(chat_id, media_url, caption)
            elif media_type == "audio":
                await self.telegram_client.send_audio(chat_id, media_url, caption)
            elif media_type == "document":
                 await self.telegram_client.send_document(chat_id, media_url, caption)
            elif media_type == "sticker":
                await self.telegram_client.send_sticker(chat_id, media_url)


class LocationMessageBlockHandler:
    """
    Handles location messages
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_location_message(
        self,
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
            latitude = get_template(str(latitude_template)).render(variables=variables)
            longitude = get_template(str(longitude_template)).render(variables=variables)
            logging_client.info(
                f"Location received latitude: {latitude}, longitude: {longitude}. User message was: {user_message}"
            )

    @handle_exceptions
    async def handle_send_location(
        self,
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
            latitude = get_template(str(latitude_template)).render(variables=variables)
            longitude = get_template(str(longitude_template)).render(variables=variables)
            logging_client.info(
                f"Sending location latitude: {latitude} and longitude: {longitude} to chat_id: {chat_id}. User message was: {user_message}"
            )
            await self.telegram_client.send_location(
                chat_id, float(latitude), float(longitude)
            )

class ContactMessageBlockHandler:
    """
    Handles contact messages
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client
    @handle_exceptions
    async def handle_contact_message(
        self,
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
            phone_number = get_template(phone_number_template).render(variables=variables)
            logging_client.info(
                f"User sent contact with number: {phone_number}. User message was: {user_message}"
            )

    @handle_exceptions
    async def handle_send_contact(
        self,
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
            phone_number = get_template(phone_number_template).render(variables=variables)
            first_name = get_template(first_name_template).render(variables=variables) if first_name_template else ""
            last_name = get_template(last_name_template).render(variables=variables) if last_name_template else ""
            logging_client.info(
                f"Sending contact with number: {phone_number} to chat_id: {chat_id}. User message was: {user_message}"
            )
            await self.telegram_client.send_contact(
                chat_id, phone_number, first_name, last_name=last_name
            )

class VenueMessageBlockHandler:
    """
    Handles venue messages
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_venue_message(
        self,
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
            address = get_template(address_template).render(variables=variables)
            logging_client.info(
                f"User sent venue with address: {address}. User message was: {user_message}"
            )
    @handle_exceptions
    async def handle_send_venue(
        self,
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
            address = get_template(address_template).render(variables=variables)
            latitude = get_template(str(latitude_template)).render(variables=variables)
            longitude = get_template(str(longitude_template)).render(variables=variables)
            title = get_template(title_template).render(variables=variables) if title_template else ""
            logging_client.info(
                f"Sending venue with address: {address}, latitude: {latitude} and longitude: {longitude} to chat_id: {chat_id}. User message was: {user_message}"
            )
            await self.telegram_client.send_venue(
                chat_id, float(latitude), float(longitude), title, address
            )

class GameMessageBlockHandler:
    """
    Handles game messages
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_game_message(
        self,
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
            game_short_name = get_template(game_short_name_template).render(variables=variables)
            logging_client.info(
                f"User sent game with short name: {game_short_name}. User message was: {user_message}"
            )
    @handle_exceptions
    async def handle_send_game(
        self,
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
            game_short_name = get_template(game_short_name_template).render(variables=variables)
            logging_client.info(
                f"Sending game with short name: {game_short_name} to chat_id: {chat_id}. User message was: {user_message}"
            )
            await self.telegram_client.send_game(chat_id, game_short_name)

class PollMessageBlockHandler:
    """
    Handles poll messages
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_poll_message(
        self,
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
            question = get_template(question_template).render(variables=variables)
            options = content.get("options", [])
            parsed_options = [
                get_template(option).render(variables=variables) for option in options
            ]
            logging_client.info(
                f"User sent poll with question: {question} and options: {parsed_options} to chat_id: {chat_id}. User message was: {user_message}"
            )

    @handle_exceptions
    async def handle_send_poll(
        self,
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
            question = get_template(question_template).render(variables=variables)
            parsed_options = [
                get_template(option).render(variables=variables) for option in options
            ]
            logging_client.info(
                f"Sending poll with question: {question} and options: {parsed_options} to chat_id: {chat_id}. User message was: {user_message}"
            )
            await self.telegram_client.send_poll(
                chat_id, question, parsed_options
            )