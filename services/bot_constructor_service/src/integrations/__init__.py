from .telegram.telegram_api import TelegramAPI
from .logging_client import LoggingClient
from .auth_service import AuthService
from .auth_service.client import get_current_user  # Добавлен импорт get_current_user

__all__ = ["TelegramAPI", "LoggingClient", "AuthService", "get_current_user"]  # Добавлен "get_current_user"
