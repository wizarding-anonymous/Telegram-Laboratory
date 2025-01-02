from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """
    Schema for successful operation responses.
    """
    message: str = Field(..., description="Success message describing the operation")
    data: Optional[Any] = Field(None, description="Additional data related to the operation")


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    """
    detail: str = Field(..., description="Error message describing the failure")


class HealthCheckResponse(BaseModel):
    """
    Schema for health check responses.
    """
    status: str = Field(..., description="Overall status of the service ('ok' or 'error')")
    details: str = Field(..., description="Detailed information about the health check")


class PaginatedResponse(BaseModel):
    """
    Schema for paginated API responses.
    """
    total: int = Field(..., description="Total number of items")
    items: List[Any] = Field(..., description="List of items in the current page")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")

class ListResponse(BaseModel):
    """
     Schema for list responses.
    """
    items: List[Any] = Field(..., description="List of items returned by the API")
    