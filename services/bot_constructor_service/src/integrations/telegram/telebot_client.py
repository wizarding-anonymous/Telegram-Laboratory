from typing import Any, Dict, List, Optional
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException
from src.core.utils import handle_exceptions


class TelebotClient(TelegramClient):
    """
    Client for interacting with the Telegram Bot API using telebot.
    """

    def __init__(self, bot_token: str = None):
        super().__init__(bot_token)
        self.bot = telebot.TeleBot(self.bot_token, parse_mode="HTML")
        logger.info("TelebotClient initialized")
    
    @handle_exceptions
    async def check_connection(self, bot_token: str = None) -> bool:
        """
        Validate telegram token using telebot.
        Args:
           bot_token(str): Token for telegram bot.
          Returns:
            bool: true if connection successful, otherwise false
        """
        token = bot_token or self.bot_token
        try:
            bot = telebot.TeleBot(token)
            bot_info = await asyncio.to_thread(bot.get_me)
            if bot_info:
                logger.info(f"Telebot token is valid for user: {bot_info.username}")
                return True
            else:
                 logger.error("Telebot token is invalid")
                 return False
        except Exception as e:
              logger.error(f"Telebot token is invalid, exception: {e}")
              return False
    
    @handle_exceptions
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: Optional[List[List[str]]] = None, inline_keyboard: Optional[List[List[Dict[str, Any]]]] = None) -> dict:
        """
        Send a message to a Telegram chat using telebot.

        Args:
            chat_id (int): Chat ID to send the message to.
            text (str): Message text.
            parse_mode (str): Formatting style for the message (e.g., "Markdown", "HTML").
            reply_markup (Optional[Any]): Reply keyboard markup
            inline_keyboard (Optional[Any]): Inline keyboard markup
        Returns:
            dict: Response from the Telegram API.
        """
        try:
            if reply_markup:
                keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
                for row in reply_markup:
                    keyboard.add(*[KeyboardButton(text=button) for button in row])
                sent_message = await asyncio.to_thread(self.bot.send_message, chat_id, text, parse_mode=parse_mode, reply_markup=keyboard)
            elif inline_keyboard:
                keyboard = InlineKeyboardMarkup(row_width=3)
                for row in inline_keyboard:
                    keyboard.add(*[InlineKeyboardButton(text=button["text"], callback_data=button["callback_data"]) for button in row])
                sent_message = await asyncio.to_thread(self.bot.send_message, chat_id, text, parse_mode=parse_mode, reply_markup=keyboard)
            else:
                sent_message = await asyncio.to_thread(self.bot.send_message, chat_id, text, parse_mode=parse_mode)
            logger.info(f"Message sent to chat {chat_id}: {text}")
            return sent_message.json
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise TelegramAPIException(detail=f"Failed to send message: {e}")
    
    @handle_exceptions
    async def send_photo(self, chat_id: int, photo_url: str, caption: Optional[str] = None) -> dict:
         """
         Sends a photo to a Telegram chat using telebot.

         Args:
             chat_id (int): Chat ID to send the photo to.
             photo_url (str): URL of the photo.
             caption (str): Optional caption for the photo.

         Returns:
             dict: Response from the Telegram API.
         """
         try:
            sent_message = await asyncio.to_thread(self.bot.send_photo, chat_id, photo_url, caption=caption)
            logger.info(f"Photo sent to chat {chat_id}: {photo_url}")
            return sent_message.json
         except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            raise TelegramAPIException(detail=f"Failed to send photo: {e}")

    @handle_exceptions
    async def send_video(self, chat_id: int, video_url: str, caption: Optional[str] = None) -> dict:
         """
         Sends a video to a Telegram chat using telebot.

         Args:
             chat_id (int): Chat ID to send the video to.
             video_url (str): URL of the video.
             caption (str): Optional caption for the video.

         Returns:
             dict: Response from the Telegram API.
         """
         try:
            sent_message = await asyncio.to_thread(self.bot.send_video, chat_id, video_url, caption=caption)
            logger.info(f"Video sent to chat {chat_id}: {video_url}")
            return sent_message.json
         except Exception as e:
             logger.error(f"Failed to send video: {e}")
             raise TelegramAPIException(detail=f"Failed to send video: {e}")


    async def send_audio(self, chat_id: int, audio_url: str, caption: Optional[str] = None) -> dict:
         """
         Sends an audio to a Telegram chat using telebot.

         Args:
             chat_id (int): Chat ID to send the audio to.
             audio_url (str): URL of the audio.
             caption (str): Optional caption for the audio.

         Returns:
             dict: Response from the Telegram API.
         """
         try:
            sent_message = await asyncio.to_thread(self.bot.send_audio, chat_id, audio_url, caption=caption)
            logger.info(f"Audio sent to chat {chat_id}: {audio_url}")
            return sent_message.json
         except Exception as e:
              logger.error(f"Failed to send audio: {e}")
              raise TelegramAPIException(detail=f"Failed to send audio: {e}")

    async def send_document(self, chat_id: int, document_url: str, caption: Optional[str] = None) -> dict:
         """
         Sends a document to a Telegram chat using telebot.

         Args:
             chat_id (int): Chat ID to send the document to.
             document_url (str): URL of the document.
             caption (str): Optional caption for the document.

         Returns:
             dict: Response from the Telegram API.
         """
         try:
            sent_message = await asyncio.to_thread(self.bot.send_document, chat_id, document_url, caption=caption)
            logger.info(f"Document sent to chat {chat_id}: {document_url}")
            return sent_message.json
         except Exception as e:
             logger.error(f"Failed to send document: {e}")
             raise TelegramAPIException(detail=f"Failed to send document: {e}")

    async def send_location(self, chat_id: int, latitude: float, longitude: float) -> dict:
        """
        Sends a location to a Telegram chat using telebot.
        Args:
            chat_id (int): Chat ID to send the location to.
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
        Returns:
            dict: Response from the Telegram API.
        """
        try:
            sent_message = await asyncio.to_thread(self.bot.send_location, chat_id, latitude, longitude)
            logger.info(f"Location sent to chat {chat_id}: lat={latitude}, lon={longitude}")
            return sent_message.json
        except Exception as e:
            logger.error(f"Failed to send location: {e}")
            raise TelegramAPIException(detail=f"Failed to send location: {e}")
    
    async def send_sticker(self, chat_id: int, sticker_url: str) -> dict:
        """
        Sends a sticker to a Telegram chat using telebot.
        Args:
            chat_id (int): Chat ID to send the sticker to.
            sticker_url (str): Url of the sticker
        Returns:
             dict: Response from the Telegram API.
        """
        try:
            sent_message = await asyncio.to_thread(self.bot.send_sticker, chat_id, sticker_url)
            logger.info(f"Sticker sent to chat {chat_id}: {sticker_url}")
            return sent_message.json
        except Exception as e:
            logger.error(f"Failed to send sticker: {e}")
            raise TelegramAPIException(detail=f"Failed to send sticker: {e}")

    async def send_contact(self, chat_id: int, phone_number: str, first_name: str, last_name: str = "") -> dict:
        """
        Sends a contact to a Telegram chat using telebot.
        Args:
             chat_id (int): Chat ID to send the contact to.
             phone_number (str): Phone number of the contact
             first_name (str): First name of the contact.
             last_name (str): Last name of the contact.
        Returns:
            dict: Response from the Telegram API.
        """
        try:
            sent_message = await asyncio.to_thread(self.bot.send_contact, chat_id, phone_number, first_name, last_name=last_name)
            logger.info(f"Contact sent to chat {chat_id}: {phone_number}")
            return sent_message.json
        except Exception as e:
            logger.error(f"Failed to send contact: {e}")
            raise TelegramAPIException(detail=f"Failed to send contact: {e}")


    async def send_venue(self, chat_id: int, latitude: float, longitude: float, title: str, address: str) -> dict:
        """
        Sends a venue to a Telegram chat using telebot.
        Args:
            chat_id (int): Chat ID to send the location to.
            latitude (float): Latitude of the venue.
            longitude (float): Longitude of the venue.
            title (str): Title of the venue.
            address (str): Address of the venue.
        Returns:
            dict: Response from the Telegram API.
        """
        try:
            sent_message = await asyncio.to_thread(self.bot.send_venue, chat_id, latitude, longitude, title, address)
            logger.info(f"Venue sent to chat {chat_id}: {address}")
            return sent_message.json
        except Exception as e:
            logger.error(f"Failed to send venue: {e}")
            raise TelegramAPIException(detail=f"Failed to send venue: {e}")

    async def send_game(self, chat_id: int, game_short_name: str) -> dict:
        """
        Sends a game to a Telegram chat using telebot.
        Args:
            chat_id (int): Chat ID to send the game to.
            game_short_name (str): Short name of the game.
        Returns:
            dict: Response from the Telegram API.
        """
        try:
            sent_message = await asyncio.to_thread(self.bot.send_game, chat_id, game_short_name)
            logger.info(f"Game sent to chat {chat_id}: {game_short_name}")
            return sent_message.json
        except Exception as e:
            logger.error(f"Failed to send game: {e}")
            raise TelegramAPIException(detail=f"Failed to send game: {e}")

    async def send_poll(self, chat_id: int, question: str, options: List[str]) -> dict:
        """
        Sends a poll to a Telegram chat using telebot.
        Args:
            chat_id (int): Chat ID to send the poll to.
            question (str): Question for the poll.
            options (List[str]): List of options.
        Returns:
            dict: Response from the Telegram API.
        """
        try:
             sent_message = await asyncio.to_thread(self.bot.send_poll, chat_id, question, options, is_anonymous=False)
             logger.info(f"Poll sent to chat {chat_id}: {question}")
             return sent_message.json
        except Exception as e:
             logger.error(f"Failed to send poll: {e}")
             raise TelegramAPIException(detail=f"Failed to send poll: {e}")

    @handle_exceptions
    async def set_webhook(self, url: str) -> bool:
        """Sets a webhook for the bot."""
        try:
            await asyncio.to_thread(self.bot.set_webhook, url=url)
            logger.info(f"Webhook was set successfully, url: {url}")
            return True
        except Exception as e:
            logger.error(f"Webhook was not set, error: {e}")
            return False
    
    @handle_exceptions
    async def delete_webhook(self) -> bool:
        """Deletes a webhook for the bot."""
        try:
             await asyncio.to_thread(self.bot.delete_webhook)
             logger.info(f"Webhook was deleted successfully")
             return True
        except Exception as e:
            logger.error(f"Webhook was not deleted, error: {e}")
            return False
    
    @handle_exceptions
    async def get_chat_members(self, chat_id: int) -> List[Dict[str, Any]]:
         """
         Get list of chat members.
         Args:
             chat_id (int): Chat ID to get chat members from.
         Returns:
             List[Dict[str,Any]]: List of chat members info
         """
         try:
              chat_members = await asyncio.to_thread(self.bot.get_chat_members_count, chat_id)
              logger.info(f"Chat members were retrieved successfully from chat_id {chat_id}")
              return [{"members_count": chat_members}]
         except Exception as e:
            logger.error(f"Failed to get chat members: {e}")
            raise TelegramAPIException(detail=f"Failed to get chat members: {e}")

    @handle_exceptions
    async def ban_chat_member(self, chat_id: int, user_id: int) -> None:
        """Bans a user from a chat."""
        try:
            await asyncio.to_thread(self.bot.ban_chat_member, chat_id, user_id)
            logger.info(f"User {user_id} banned from chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to ban user {user_id} from chat {chat_id}: {e}")
            raise TelegramAPIException(detail=f"Failed to ban user {user_id} from chat {chat_id}: {e}")

    @handle_exceptions
    async def unban_chat_member(self, chat_id: int, user_id: int) -> None:
        """Unbans a user from a chat."""
        try:
            await asyncio.to_thread(self.bot.unban_chat_member, chat_id, user_id)
            logger.info(f"User {user_id} unbanned from chat {chat_id}")
        except Exception as e:
             logger.error(f"Failed to unban user {user_id} from chat {chat_id}: {e}")
             raise TelegramAPIException(detail=f"Failed to unban user {user_id} from chat {chat_id}: {e}")

    @handle_exceptions
    async def set_chat_title(self, chat_id: int, title: str) -> None:
        """Sets a title for a chat."""
        try:
            await asyncio.to_thread(self.bot.set_chat_title, chat_id, title)
            logger.info(f"Set title to chat {chat_id} : {title}")
        except Exception as e:
            logger.error(f"Failed to set chat title for chat {chat_id}: {e}")
            raise TelegramAPIException(detail=f"Failed to set chat title for chat {chat_id}: {e}")

    @handle_exceptions
    async def set_chat_description(self, chat_id: int, description: str) -> None:
        """Sets a description for a chat."""
        try:
            await asyncio.to_thread(self.bot.set_chat_description, chat_id, description)
            logger.info(f"Set chat description for chat {chat_id} : {description}")
        except Exception as e:
             logger.error(f"Failed to set chat description for chat {chat_id}: {e}")
             raise TelegramAPIException(detail=f"Failed to set chat description for chat {chat_id}: {e}")
    
    @handle_exceptions
    async def pin_chat_message(self, chat_id: int, message_id: int) -> None:
        """Pins a message in a chat."""
        try:
            await asyncio.to_thread(self.bot.pin_chat_message, chat_id, message_id)
            logger.info(f"Message {message_id} pinned in chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to pin message {message_id} in chat {chat_id}: {e}")
            raise TelegramAPIException(detail=f"Failed to pin message {message_id} in chat {chat_id}: {e}")

    @handle_exceptions
    async def unpin_chat_message(self, chat_id: int, message_id: int) -> None:
        """Unpins a message in a chat."""
        try:
            await asyncio.to_thread(self.bot.unpin_chat_message, chat_id, message_id)
            logger.info(f"Message {message_id} unpinned in chat {chat_id}")
        except Exception as e:
             logger.error(f"Failed to unpin message {message_id} in chat {chat_id}: {e}")
             raise TelegramAPIException(detail=f"Failed to unpin message {message_id} in chat {chat_id}: {e}")
    
    async def close(self) -> None:
        """Closes the telebot bot"""
        if self.bot:
            session = await asyncio.to_thread(self.bot.get_session)
            if session:
              session.close()
            logger.info("Telebot client closed")