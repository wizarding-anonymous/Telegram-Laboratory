# services/bot_constructor_service/src/api/routers/__init__.py

from .bot_router import router as bot_router
from .block_router import router as block_router
from .health_router import router as health_router

__all__ = ["bot_router", "block_router", "health_router"]
