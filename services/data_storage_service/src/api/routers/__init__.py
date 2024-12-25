# src/api/routers/__init__.py

# Импортируем все основные роутеры
from .bot_router import router as bot_router
from .health_router import router as health_router
from .metadata_router import router as metadata_router

# Экспортируем роутеры для удобства импорта в другие части проекта
__all__ = ["bot_router", "metadata_router", "health_router"]
