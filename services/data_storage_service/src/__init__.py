# src/__init__.py

# Импорт базовых настроек, компонентов и зависимостей
from .api.routers.bot_router import router as bot_router
from .api.routers.health_router import router as health_router
from .api.routers.metadata_router import router as metadata_router
from .config import settings
from .db.database import check_db_connection, close_engine, init_db
from .integrations.logging_client import LoggingClient

# Инициализация логирования
logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

# Экспорт всех основных компонентов, чтобы они были доступны при импорте пакета `src`
__all__ = [
    "settings",
    "init_db",
    "close_engine",
    "check_db_connection",
    "bot_router",
    "metadata_router",
    "health_router",
    "logging_client",
]
