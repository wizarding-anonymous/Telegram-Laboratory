from typing import Dict, Any
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """
    Schema for health check responses.
    """
    status: str = Field(..., description="Overall status of the service ('ok' or 'error')")
    details: str = Field(..., description="Detailed information about the health check")