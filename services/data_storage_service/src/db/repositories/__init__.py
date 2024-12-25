# services/data_storage_service/src/db/repositories/__init__.py

"""
Модуль инициализации (package initializer) для пакета `repositories`.

В данном модуле производится импорт всех классов-репозиториев,
ответственных за CRUD-операции над различными моделями базы данных.

Экспортируемые элементы:
    BotRepository       – Репозиторий для работы с моделью `Bot`.
    MetadataRepository  – Репозиторий для работы с моделью `Metadata`.
"""

from .bot_repository import BotRepository
from .metadata_repository import MetadataRepository

__all__ = [
    "BotRepository",
    "MetadataRepository",
]
