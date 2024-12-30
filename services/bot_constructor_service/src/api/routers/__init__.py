from .bot_router import router as bot_router
from .block_router import router as block_router
from .health_router import router as health_router
from .message_router import router as message_router
from .keyboard_router import router as keyboard_router
from .callback_router import router as callback_router
from .chat_router import router as chat_router
from .webhook_router import router as webhook_router
from .flow_router import router as flow_router
from .variable_router import router as variable_router
from .db_router import router as db_router
from .api_request_router import router as api_request_router
from .bot_settings_router import router as bot_settings_router
from .connection_router import router as connection_router


__all__ = [
    "bot_router",
    "block_router",
    "health_router",
    "message_router",
    "keyboard_router",
    "callback_router",
    "chat_router",
    "webhook_router",
    "flow_router",
    "variable_router",
    "db_router",
    "api_request_router",
    "bot_settings_router",
    "connection_router",
]