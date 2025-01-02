from typing import Optional, Any
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
    status: str = Field(..., description="Overall status of the service (ok/error)")
    details: str = Field(..., description="Detailed information about the health check")