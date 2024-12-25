# src/api/__init__.py

# Импорт роутеров из различных частей API
from .routers.bot_router import router as bot_router
from .routers.health_router import router as health_router
from .routers.metadata_router import router as metadata_router

# Экспорт всех роутеров для удобства импорта в другие части проекта
__all__ = ["bot_router", "metadata_router", "health_router"]
