from .bot_model import Bot
from .block_model import Block
from .connection_model import Connection
from src.db.database import Base  # Импортируем Base из database

__all__ = ["Bot", "Block", "Connection", "Base"]  # Экспортируем Base для использования в миграциях