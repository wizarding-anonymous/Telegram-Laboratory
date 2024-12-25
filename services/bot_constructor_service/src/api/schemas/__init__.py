# services/bot_constructor_service/src/api/schemas/__init__.py

from .bot_schema import BotCreate, BotUpdate, BotResponse, BotListResponse
from .block_schema import BlockCreate, BlockUpdate, BlockResponse, BlockConnection
from .response_schema import ErrorResponse, SuccessResponse, PaginatedResponse, HealthCheckResponse, ValidationErrorResponse, ListResponse

__all__ = [
    # Bot schemas
    "BotCreate",
    "BotUpdate",
    "BotResponse",
    "BotListResponse",
    
    # Block schemas
    "BlockCreate",
    "BlockUpdate",
    "BlockResponse",
    "BlockConnection",
    
    # Response schemas
    "ErrorResponse",
    "SuccessResponse",
    "PaginatedResponse",
    "HealthCheckResponse",
    "ValidationErrorResponse",
    "ListResponse",
]
