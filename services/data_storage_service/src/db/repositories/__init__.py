"""
Модуль инициализации (package initializer) для пакета `repositories`.

В данном модуле производится импорт всех классов-репозиториев,
ответственных за CRUD-операции над различными моделями базы данных.

Экспортируемые элементы:
    BotRepository       – Репозиторий для работы с моделью `Bot`.
    MetadataRepository  – Репозиторий для работы с моделью `Metadata`.
    SchemaRepository    – Репозиторий для работы с моделью `Schema`.
"""

from .bot_repository import BotRepository
from .metadata_repository import MetadataRepository
from .schema_repository import SchemaRepository

__all__ = [
    "BotRepository",
    "MetadataRepository",
    "SchemaRepository"
]