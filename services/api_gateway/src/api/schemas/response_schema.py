# services\api_gateway\src\api\schemas\response_schema.py
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, validator
from enum import Enum

T = TypeVar('T')

class ServiceStatus(str, Enum):
    """Enum для статуса сервиса."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    MAINTENANCE = "maintenance"

class ErrorResponse(BaseModel):
    """Базовая модель для ответов с ошибками."""
    error_code: int = Field(..., description="HTTP код ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительные детали ошибки")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())
    trace_id: Optional[str] = Field(None, description="ID для отслеживания ошибки")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error_code": 404,
                "message": "Resource not found",
                "details": {"path": "/api/v1/users/123"},
                "timestamp": "2024-01-01T12:00:00Z",
                "trace_id": "abc123xyz789"
            }
        }
    }

class ValidationErrorDetail(BaseModel):
    """Модель для деталей ошибки валидации."""
    field: str = Field(..., description="Поле с ошибкой")
    message: str = Field(..., description="Сообщение об ошибке")
    location: Optional[str] = Field(None, description="Место возникновения ошибки")

class ValidationErrorResponse(ErrorResponse):
    """Модель для ошибок валидации."""
    validation_errors: List[ValidationErrorDetail] = Field(..., description="Список ошибок валидации")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error_code": 422,
                "message": "Validation error",
                "validation_errors": [
                    {
                        "field": "email",
                        "message": "invalid email format",
                        "location": "body"
                    }
                ],
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    }

class SuccessResponse(BaseModel):
    """Базовая модель для успешных ответов."""
    message: str = Field(..., description="Сообщение об успешном выполнении")
    data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Operation completed successfully",
                "data": {"id": 123},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    }

class PaginatedResponse(BaseModel, Generic[T]):
    """Модель для пагинированных ответов."""
    items: List[T] = Field(..., description="Список элементов")
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Общее количество страниц")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 10,
                "pages": 10,
                "has_next": True,
                "has_prev": False
            }
        }
    }

class ServiceMetrics(BaseModel):
    """Модель для метрик сервиса."""
    requests_total: int = Field(..., description="Общее количество запросов")
    requests_success: int = Field(..., description="Успешные запросы")
    requests_error: int = Field(..., description="Запросы с ошибками")
    avg_response_time: float = Field(..., description="Среднее время ответа (мс)")
    active_connections: int = Field(..., description="Активные соединения")
    last_minute_requests: int = Field(..., description="Запросы за последнюю минуту")

class ServiceHealthCheck(BaseModel):
    """Модель для проверки здоровья сервиса."""
    status: ServiceStatus = Field(..., description="Статус сервиса")
    message: Optional[str] = Field(None, description="Дополнительное сообщение")
    version: str = Field(..., description="Версия сервиса")
    uptime: float = Field(..., description="Время работы в секундах")
    last_check: datetime = Field(..., description="Время последней проверки")
    dependencies: Dict[str, ServiceStatus] = Field(..., description="Статус зависимостей")

    @validator('status')
    def validate_status(cls, v):
        if not isinstance(v, ServiceStatus):
            raise ValueError(f"Invalid status: {v}")
        return v

class MetricsResponse(BaseModel):
    """Модель для ответа с метриками системы."""
    total_requests: int = Field(..., description="Общее количество запросов")
    average_response_time: float = Field(..., description="Среднее время ответа (мс)")
    error_rate: float = Field(..., description="Процент ошибок")
    total_active_users: int = Field(..., description="Количество активных пользователей")
    cpu_usage: float = Field(..., description="Использование CPU (%)")
    memory_usage: float = Field(..., description="Использование памяти (%)")
    timestamp: datetime = Field(..., description="Время сбора метрик")

class ServiceMetricsResponse(BaseModel):
    """Модель для ответа с метриками конкретного сервиса."""
    service_name: str = Field(..., description="Название сервиса")
    requests_count: int = Field(..., description="Количество запросов")
    average_response_time: float = Field(..., description="Среднее время ответа (мс)")
    error_count: int = Field(..., description="Количество ошибок")
    success_rate: float = Field(..., description="Процент успешных запросов")
    active_connections: int = Field(..., description="Количество активных соединений")
    timestamp: datetime = Field(..., description="Время сбора метрик")

class CacheResponse(BaseModel):
    """Модель для ответов, связанных с кешированием."""
    cache_hit: bool = Field(..., description="Найдено ли значение в кеше")
    cached_at: Optional[datetime] = Field(None, description="Время кеширования")
    expires_at: Optional[datetime] = Field(None, description="Время истечения кеша")
    data: Optional[Dict[str, Any]] = Field(None, description="Закешированные данные")

class RouteResponse(BaseModel):
    """Модель для ответа с информацией о маршруте."""
    id: int = Field(..., description="ID маршрута")
    path: str = Field(..., description="Путь маршрута")
    method: str = Field(..., description="HTTP метод")
    destination_url: str = Field(..., description="URL назначения")
    auth_required: bool = Field(..., description="Требуется ли аутентификация")
    required_roles: Optional[List[str]] = Field(None, description="Требуемые роли")
    required_permissions: Optional[List[str]] = Field(None, description="Требуемые разрешения")
    is_active: bool = Field(..., description="Активен ли маршрут")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: Optional[datetime] = Field(None, description="Время последнего обновления")

    @validator('method')
    def validate_method(cls, v):
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
        if v.upper() not in valid_methods:
            raise ValueError(f"Invalid HTTP method: {v}")
        return v.upper()

class ServiceDiscoveryResponse(BaseModel):
    """Модель для ответа от Service Discovery."""
    services: List[Dict[str, Any]] = Field(..., description="Список доступных сервисов")
    timestamp: datetime = Field(..., description="Время получения данных")

class TokenResponse(BaseModel):
    """Модель для ответа с информацией о токене."""
    access_token: str = Field(..., description="Access токен")
    token_type: str = Field("Bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    refresh_token: Optional[str] = Field(None, description="Refresh токен")
    scope: Optional[str] = Field(None, description="Область действия токена")