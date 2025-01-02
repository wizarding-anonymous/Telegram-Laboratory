# Импорт интеграций с внешними сервисами
from .auth_service import AuthService
from .logging_client import LoggingClient
from .service_discovery import ServiceDiscoveryClient  # Добавляем импорт ServiceDiscoveryClient

# Экспорт всех интеграций для удобства импорта в другие части проекта
__all__ = [
    "AuthService",
    "LoggingClient",
    "ServiceDiscoveryClient", # Добавляем ServiceDiscoveryClient в список экспортируемых компонентов
]