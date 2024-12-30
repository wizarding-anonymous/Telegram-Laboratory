from .bot_model import Bot
from .block_model import Block
from .connection_model import Connection
from src.db.database import Base  # Импортируем Base из database
from .webhook_model import Webhook
from .variable_model import Variable
from .keyboard_model import Keyboard
from .callback_model import Callback
from .message_model import Message
from .database_model import Database
from .api_request_model import ApiRequest
from .media_group_model import MediaGroup
from .flow_model import Flow

__all__ = ["Bot", "Block", "Connection", "Base", "Webhook", "Variable", "Keyboard", "Callback", "Message", "Database", "ApiRequest", "MediaGroup", "Flow"]  # Экспортируем Base для использования в миграциях