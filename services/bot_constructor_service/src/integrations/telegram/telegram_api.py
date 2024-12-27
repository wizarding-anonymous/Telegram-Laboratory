from typing import Dict, Any, Optional, List
import httpx
from fastapi import HTTPException
from loguru import logger
import json

from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")

class TelegramAPI:
    """
    A client for interacting with the Telegram Bot API.
    """

    def __init__(self, client: httpx.AsyncClient = None):
         self.base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
         self.client = client or httpx.AsyncClient()
         logging_client.info("TelegramAPI initialized")

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """Makes an asynchronous request to the Telegram API."""
        url = f"{self.base_url}/{endpoint}"
        logging_client.debug(f"Making {method} request to: {url}, data: {data}, params: {params}")
        try:
            response = await self.client.request(method, url, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logging_client.error(f"HTTP Error: {exc}")
            if exc.response and exc.response.text:
                 try:
                      error_details = exc.response.json()
                      logging_client.error(f"Telegram API error: {error_details}")
                      raise HTTPException(
                         status_code=exc.response.status_code, detail=f"Telegram API Error: {error_details.get('description') or error_details}"
                       ) from exc
                 except json.JSONDecodeError:
                      logging_client.error(f"Invalid response from Telegram API: {exc.response.text}")
                      raise HTTPException(
                           status_code=exc.response.status_code, detail=f"Telegram API Error: Invalid response"
                       ) from exc
            raise HTTPException(
                    status_code=500, detail=f"Telegram API Error: {exc}"
            ) from exc
        except Exception as exc:
            logging_client.exception(f"Unexpected error: {exc}")
            raise HTTPException(status_code=500, detail="Internal server error") from exc


    @handle_exceptions
    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[List[List[Dict[str, Any]]]] = None, inline_keyboard: Optional[List[List[Dict[str, Any]]]] = None) -> Any:
        """Sends a text message to the specified chat."""
        logging_client.info(f"Sending text message to chat_id: {chat_id}")

        data = {"chat_id": chat_id, "text": text}
        if reply_markup:
                data["reply_markup"] = {"keyboard": reply_markup, "resize_keyboard": True}
        if inline_keyboard:
                data["reply_markup"] = {"inline_keyboard": inline_keyboard}

        return await self._make_request("POST", "sendMessage", data=data)

    @handle_exceptions
    async def send_photo(self, chat_id: int, photo: str, caption: Optional[str] = None) -> Any:
        """Sends a photo to the specified chat."""
        logging_client.info(f"Sending photo to chat_id: {chat_id}")

        data = {"chat_id": chat_id, "photo": photo}
        if caption:
             data["caption"] = caption

        return await self._make_request("POST", "sendPhoto", data=data)

    @handle_exceptions
    async def send_video(self, chat_id: int, video: str, caption: Optional[str] = None) -> Any:
        """Sends a video to the specified chat."""
        logging_client.info(f"Sending video to chat_id: {chat_id}")

        data = {"chat_id": chat_id, "video": video}
        if caption:
             data["caption"] = caption
        return await self._make_request("POST", "sendVideo", data=data)

    @handle_exceptions
    async def send_audio(self, chat_id: int, audio: str, caption: Optional[str] = None) -> Any:
        """Sends an audio to the specified chat."""
        logging_client.info(f"Sending audio to chat_id: {chat_id}")
        data = {"chat_id": chat_id, "audio": audio}
        if caption:
            data["caption"] = caption
        return await self._make_request("POST", "sendAudio", data=data)

    @handle_exceptions
    async def send_document(self, chat_id: int, document: str, caption: Optional[str] = None) -> Any:
        """Sends a document to the specified chat."""
        logging_client.info(f"Sending document to chat_id: {chat_id}")
        data = {"chat_id": chat_id, "document": document}
        if caption:
            data["caption"] = caption
        return await self._make_request("POST", "sendDocument", data=data)

    @handle_exceptions
    async def send_location(self, chat_id: int, latitude: float, longitude: float) -> Any:
        """Sends a location to the specified chat."""
        logging_client.info(f"Sending location to chat_id: {chat_id}")
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
        return await self._make_request("POST", "sendLocation", data=data)

    @handle_exceptions
    async def send_sticker(self, chat_id: int, sticker: str) -> Any:
        """Sends a sticker to the specified chat."""
        logging_client.info(f"Sending sticker to chat_id: {chat_id}")
        data = {"chat_id": chat_id, "sticker": sticker}
        return await self._make_request("POST", "sendSticker", data=data)

    @handle_exceptions
    async def send_contact(self, chat_id: int, phone_number: str, first_name: str, last_name: Optional[str] = None) -> Any:
        """Sends a contact to the specified chat."""
        logging_client.info(f"Sending contact to chat_id: {chat_id}")
        data = {"chat_id": chat_id, "phone_number": phone_number, "first_name": first_name}
        if last_name:
            data["last_name"] = last_name
        return await self._make_request("POST", "sendContact", data=data)
    
    @handle_exceptions
    async def send_venue(self, chat_id: int, latitude: float, longitude: float, title: str, address: str) -> Any:
        """Sends a venue to the specified chat."""
        logging_client.info(f"Sending venue to chat_id: {chat_id}")
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, "title": title, "address": address}
        return await self._make_request("POST", "sendVenue", data=data)

    @handle_exceptions
    async def send_game(self, chat_id: int, game_short_name: str) -> Any:
         """Sends a game to the specified chat."""
         logging_client.info(f"Sending game to chat_id: {chat_id}")
         data = {"chat_id": chat_id, "game_short_name": game_short_name}
         return await self._make_request("POST", "sendGame", data=data)

    @handle_exceptions
    async def send_poll(self, chat_id: int, question: str, options: List[str]) -> Any:
        """Sends a poll to the specified chat."""
        logging_client.info(f"Sending poll to chat_id: {chat_id}")
        data = {"chat_id": chat_id, "question": question, "options": options}
        return await self._make_request("POST", "sendPoll", data=data)

    @handle_exceptions
    async def set_webhook(self, url: str) -> Any:
         """Sets a webhook for the bot."""
         logging_client.info(f"Setting webhook url: {url}")
         data = {"url": url}
         return await self._make_request("POST", "setWebhook", data=data)
    
    @handle_exceptions
    async def delete_webhook(self) -> Any:
         """Deletes a webhook for the bot."""
         logging_client.info("Deleting webhook")
         return await self._make_request("POST", "deleteWebhook")
    
    @handle_exceptions
    async def get_webhook_info(self) -> Any:
        """Gets webhook info for the bot."""
        logging_client.info("Getting webhook info")
        return await self._make_request("GET", "getWebhookInfo")

    @handle_exceptions
    async def get_updates(self, offset: Optional[int] = None, limit: Optional[int] = None, timeout: Optional[int] = None) -> Any:
        """Gets updates for the bot."""
        logging_client.info("Getting updates from Telegram API")
        params = {}
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        if timeout:
            params["timeout"] = timeout
        return await self._make_request("GET", "getUpdates", params=params)

    async def close(self) -> None:
        """Closes the httpx client"""
        if self.client:
              await self.client.aclose()
              logging_client.info("Telegram client closed")