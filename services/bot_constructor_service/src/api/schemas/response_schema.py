from pydantic import BaseModel, Field, validator
from typing import Any, List, Optional
from src.core.utils.validators import validate_status  # Импорт валидатора

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error_code: int = Field(..., description="Error code associated with the failure")
    message: str = Field(..., description="Error message describing the failure")
    details: Optional[Any] = Field(None, description="Additional details about the error")


class SuccessResponse(BaseModel):
    """Schema for successful operation responses."""
    message: str = Field(..., description="Success message describing the operation")
    data: Optional[Any] = Field(None, description="Additional data related to the operation")


class PaginatedResponse(BaseModel):
    """Schema for paginated API responses."""
    total: int = Field(..., description="Total number of items")
    items: List[Any] = Field(..., description="List of items in the current page")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")


class HealthCheckResponse(BaseModel):
    """Schema for health check responses."""
    status: str = Field(..., description="Overall status of the service ('ok', 'degraded', 'unhealthy')")
    details: dict = Field(..., description="Detailed status of dependent services")
    version: str = Field(..., description="Version of the service")

    @validator("status")
    def validate_status_field(cls, value):
        return validate_status(value)  # Валидация через валидатор

    @validator("version")
    def validate_version_field(cls, value):
        from src.core.utils.validators import validate_version  # Импорт валидатора
        return validate_version(value)  # Валидация версии


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    field: str = Field(..., description="Name of the field that caused the validation error")
    message: str = Field(..., description="Validation error message")


class ListResponse(BaseModel):
    """Schema for returning a list of items."""
    items: List[Any] = Field(..., description="List of items returned by the API")
    total: int = Field(..., description="Total number of items available")
