from .telegram.telegram_api_client import TelegramAPI
from .logging_client import LoggingClient
from .auth_service import AuthService
from .auth_service.client import get_current_user
from .redis_client import redis_client
from .telegram.aiogram_client import AiogramClient
from .telegram.telebot_client import TelebotClient
from .data_storage_client import DataStorageClient
from .telegram.client import TelegramClient


def get_telegram_client(library: str) -> TelegramClient:
    """
    Returns a Telegram client based on the specified library.

    Args:
        library (str): The name of the library to use ('telegram_api', 'aiogram', 'telebot').

    Returns:
         TelegramClient: An instance of the appropriate Telegram client.

    Raises:
        ValueError: If an invalid library name is provided.
    """
    if library == "telegram_api":
        return TelegramAPI()
    elif library == "aiogram":
        return AiogramClient()
    elif library == "telebot":
        return TelebotClient()
    else:
        raise ValueError(f"Invalid telegram library: {library}")


__all__ = [
    "TelegramAPI",
    "LoggingClient",
    "AuthService",
    "get_current_user",
    "redis_client",
    "AiogramClient",
    "TelebotClient",
    "DataStorageClient",
    "get_telegram_client",
    "TelegramClient"
]