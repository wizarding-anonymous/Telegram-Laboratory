from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """
    Schema for successful operation response.
    """
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    """
    Schema for error response.
    """
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Detailed error information")


class HealthCheckResponse(BaseModel):
    """
    Schema for health check response.
    """
    status: str = Field(..., description="Status of the service (ok/error)")
    details: str = Field(..., description="Detailed information about the health check")


class PaginatedResponse(BaseModel):
    """
    Schema for paginated responses.
    """
    items: List[BaseModel] = Field(..., description="List of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")


class ListResponse(BaseModel):
    """
     Schema for list responses.
    """
    items: List[BaseModel] = Field(..., description="List of items")