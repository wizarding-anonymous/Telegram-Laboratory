# src/integrations/__init__.py

# Импорт интеграций с внешними сервисами
from .auth_service import AuthService
from .logging_client import LoggingClient
from .telegram import TelegramClient  # Добавляем импорт TelegramClient

# Экспорт всех интеграций для удобства импорта в другие части проекта
__all__ = [
    "AuthService",
    "LoggingClient",
    "TelegramClient",  # Добавляем TelegramClient в список экспортируемых компонентов
]
