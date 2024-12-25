# src/api/schemas/__init__.py

# Импорт моделей
from .bot_schema import BotCreate, BotListResponse, BotResponse, BotUpdate
from .metadata_schema import MetadataCreate, MetadataResponse, MetadataUpdate
from .response_schema import (ErrorResponse, HealthCheckResponse, ListResponse,
                            PaginatedResponse, SuccessResponse, ValidationErrorResponse)

# Экспорт всех моделей для удобства импорта в другие части проекта
__all__ = [
    "BotCreate",
    "BotUpdate",
    "BotResponse",
    "BotListResponse",
    "MetadataCreate",
    "MetadataUpdate", 
    "MetadataResponse",
    "SuccessResponse",
    "ErrorResponse",
    "HealthCheckResponse",
    "PaginatedResponse",
    "ListResponse",
    "ValidationErrorResponse",
]