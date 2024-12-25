# src/api/controllers/__init__.py

# Импортируем контроллеры для работы с различными ресурсами
from .bot_controller import BotController
from .health_controller import HealthController
from .metadata_controller import MetadataController

# Экспортируем контроллеры для удобства импорта в другие части проекта
__all__ = ["BotController", "MetadataController", "HealthController"]
