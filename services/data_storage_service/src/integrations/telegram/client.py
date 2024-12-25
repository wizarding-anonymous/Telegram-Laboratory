# services\data_storage_service\src\integrations\telegram\client.py
# import httpx
import os

from loguru import logger


class TelegramClient:
    """
    Клиент для взаимодействия с Telegram API.
    """

    def __init__(self, bot_token: str = None):
        """
        Инициализация клиента для Telegram API.

        Args:
            bot_token (str): Токен для доступа к Telegram боту.
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("Telegram bot token is required")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        logger.info("TelegramClient initialized")

    async def check_connection(self):
        """
        Проверка доступности Telegram API с использованием метода getMe.

        Возвращает:
            bool: True, если подключение успешно, иначе False.
        """
        url = f"{self.base_url}/getMe"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.status_code == 200
