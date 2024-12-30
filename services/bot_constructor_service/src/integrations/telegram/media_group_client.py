from typing import List, Dict, Any
from abc import ABC, abstractmethod
from src.core.utils import handle_exceptions
import httpx
import asyncio
import json

class AbstractMediaGroupClient(ABC):
    """
    Abstract base class for sending media groups via Telegram API.
    """

    @abstractmethod
    async def send_media_group(self, chat_id: int, media: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Abstract method for sending media groups.

        Args:
            chat_id (int): Telegram chat ID.
            media (List[Dict[str, Any]]): List of media items to send.
        
        Returns:
              List[Dict[str, Any]]: List of sent messages info
        """
        pass


class TelegramAPIMediaGroupClient(AbstractMediaGroupClient):
    """
    Implementation for sending media groups using the Telegram Bot API directly.
    """

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.client = httpx.AsyncClient()

    @handle_exceptions
    async def send_media_group(self, chat_id: int, media: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
          """
          Sends a media group using the Telegram Bot API directly.

          Args:
                chat_id (int): Telegram chat ID.
                media (List[Dict[str, Any]]): List of media items to send.
            Returns:
                List[Dict[str, Any]]: List of sent messages info
          """
          
          
          media_items = []
          for item in media:
            media_type = item.get("type")
            if media_type == "photo":
              media_items.append({"type": "photo", "media":item.get("media"), "caption": item.get("caption")})
            elif media_type == "video":
               media_items.append({"type": "video", "media":item.get("media"), "caption": item.get("caption")})
            elif media_type == "audio":
               media_items.append({"type": "audio", "media":item.get("media"), "caption": item.get("caption")})
            elif media_type == "document":
              media_items.append({"type": "document", "media":item.get("media"), "caption": item.get("caption")})

          payload = {
              "chat_id": chat_id,
              "media": json.dumps(media_items),
          }

          response = await self.client.post(
            url=f"{self.base_url}/sendMediaGroup",
            data = payload
          )
          response.raise_for_status()
          
          messages = response.json().get('result', [])
          
          if not isinstance(messages, list):
            messages = [messages]
          
          messages_info = [{"message_id": item.get("message_id")} for item in messages]
          return messages_info
    
class AiogramMediaGroupClient(AbstractMediaGroupClient):
    """
    Implementation for sending media groups using aiogram library.
    """
    def __init__(self, bot_token: str):
        try:
            from aiogram import Bot
        except ImportError:
              raise ImportError("Please install aiogram to use this client. pip install aiogram")
        self.bot = Bot(token=bot_token)


    @handle_exceptions
    async def send_media_group(self, chat_id: int, media: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
             Sends a media group using aiogram library

            Args:
                 chat_id (int): Telegram chat ID.
                 media (List[Dict[str, Any]]): List of media items to send.
            Returns:
                 List[Dict[str, Any]]: List of sent messages info
            """
            try:
              from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
            except ImportError:
              raise ImportError("Please install aiogram to use this client. pip install aiogram")
            
            media_items = []
            for item in media:
              media_type = item.get("type")
              if media_type == "photo":
                media_items.append(InputMediaPhoto(media=item.get("media"), caption=item.get("caption")))
              elif media_type == "video":
                 media_items.append(InputMediaVideo(media=item.get("media"), caption=item.get("caption")))
              elif media_type == "audio":
                  media_items.append(InputMediaAudio(media=item.get("media"), caption=item.get("caption")))
              elif media_type == "document":
                 media_items.append(InputMediaDocument(media=item.get("media"), caption=item.get("caption")))

            sent_messages = await self.bot.send_media_group(chat_id=chat_id, media=media_items)
            
            messages_info = [{"message_id": item.message_id} for item in sent_messages]
            return messages_info


class TelebotMediaGroupClient(AbstractMediaGroupClient):
    """
    Implementation for sending media groups using pyTelegramBotAPI (telebot) library.
    """
    def __init__(self, bot_token: str):
        try:
            import telebot
        except ImportError:
              raise ImportError("Please install pyTelegramBotAPI to use this client. pip install pyTelegramBotAPI")
        self.bot = telebot.TeleBot(bot_token)

    @handle_exceptions
    async def send_media_group(self, chat_id: int, media: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sends a media group using pyTelegramBotAPI (telebot) library

         Args:
              chat_id (int): Telegram chat ID.
              media (List[Dict[str, Any]]): List of media items to send.
         Returns:
              List[Dict[str, Any]]: List of sent messages info
        """
        try:
           import telebot
        except ImportError:
              raise ImportError("Please install pyTelegramBotAPI to use this client. pip install pyTelegramBotAPI")
        
        media_items = []
        for item in media:
              media_type = item.get("type")
              if media_type == "photo":
                 media_items.append(telebot.types.InputMediaPhoto(media=item.get("media"), caption=item.get("caption")))
              elif media_type == "video":
                 media_items.append(telebot.types.InputMediaVideo(media=item.get("media"), caption=item.get("caption")))
              elif media_type == "audio":
                 media_items.append(telebot.types.InputMediaAudio(media=item.get("media"), caption=item.get("caption")))
              elif media_type == "document":
                  media_items.append(telebot.types.InputMediaDocument(media=item.get("media"), caption=item.get("caption")))
        
        sent_messages = await asyncio.to_thread(self.bot.send_media_group, chat_id, media_items)
        messages_info = [{"message_id": item.message_id} for item in sent_messages]
        
        return messages_info