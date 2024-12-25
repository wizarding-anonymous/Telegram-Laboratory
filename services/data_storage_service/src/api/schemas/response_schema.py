# services\data_storage_service\src\api\schemas\response_schema.py
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar('T')


class SuccessResponse(BaseModel):
    """
    Схема для успешных ответов от API.
    """
    message: str = Field(..., description="Сообщение об успешной операции.")
    data: Optional[Any] = Field(
        None, description="Дополнительные данные, связанные с операцией."
    )
    migrations_status: Optional[str] = Field(
        None, description="Статус миграций для базы данных бота"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Operation successful",
                "data": {"id": 1, "name": "MyAwesomeBot"},
                "migrations_status": "Migrations applied successfully",
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Схема для ошибок в ответах API.
    """
    error_code: int = Field(..., description="Код ошибки")
    message: str = Field(..., description="Сообщение ошибки")
    details: Optional[Any] = Field(None, description="Дополнительные детали об ошибке")
    migration_error_details: Optional[str] = Field(
        None, description="Детали ошибки миграции, если применимо"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "error_code": 404,
                "message": "Resource not found",
                "details": {"bot_id": 999},
                "migration_error_details": "Migration failed for bot database",
            }
        }
    }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Схема для пагинированных ответов от API.
    """
    total: int = Field(..., description="Общее количество элементов")
    items: List[T] = Field(..., description="Список элементов на текущей странице")
    page: int = Field(..., description="Номер текущей страницы")
    size: int = Field(..., description="Количество элементов на странице")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 100,
                "items": [{"id": 1, "name": "Bot 1"}, {"id": 2, "name": "Bot 2"}],
                "page": 1,
                "size": 10,
            }
        }
    }


class HealthCheckResponse(BaseModel):
    """
    Схема для ответов на запросы состояния сервиса (Health Check).
    """
    status: str = Field(
        ..., description="Общий статус сервиса (healthy, degraded, unhealthy)"
    )
    details: Dict[str, Any] = Field(
        ..., description="Подробности о состоянии зависимостей сервиса"
    )
    version: str = Field(..., description="Версия микросервиса")
    migrations: Optional[str] = Field(None, description="Статус миграций")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        valid_statuses = ["healthy", "degraded", "unhealthy"]
        if value not in valid_statuses:
            raise ValueError(
                f"Invalid status: '{value}'. Must be one of {valid_statuses}."
            )
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "details": {
                    "database": {
                        "status": "healthy",
                        "message": "Database connection is active",
                    },
                    "telegram_api": {
                        "status": "healthy",
                        "message": "Telegram API is accessible",
                    },
                    "auth_service": {
                        "status": "healthy",
                        "message": "Auth Service is accessible",
                    },
                },
                "version": "1.0.0",
                "migrations": "Migrations applied successfully",
            }
        }
    }


class ValidationErrorResponse(BaseModel):
    """
    Схема для ошибок валидации.
    """
    field: str = Field(..., description="Название поля, в котором произошла ошибка")
    message: str = Field(..., description="Сообщение об ошибке валидации")

    model_config = {
        "json_schema_extra": {
            "example": {"field": "name", "message": "Name cannot be empty"}
        }
    }


class ListResponse(BaseModel, Generic[T]):
    """
    Схема для возврата списка элементов (например, ботов).
    """
    items: List[T] = Field(..., description="Список элементов")
    total: int = Field(..., description="Общее количество элементов")

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [{"id": 1, "name": "MyBot"}, {"id": 2, "name": "AnotherBot"}],
                "total": 2,
            }
        }
    }