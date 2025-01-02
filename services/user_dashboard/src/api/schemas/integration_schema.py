from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IntegrationCreate(BaseModel):
    """
    Schema for creating a new integration.
    """
    service: str = Field(..., description="Name of the integration service")
    api_key: str = Field(..., description="API key for the integration")


class IntegrationUpdate(BaseModel):
    """
    Schema for updating an existing integration.
    """
    service: Optional[str] = Field(None, description="Updated name of the integration service")
    api_key: Optional[str] = Field(None, description="Updated API key for the integration")


class IntegrationResponse(BaseModel):
    """
    Schema for an integration response.
    """
    id: int = Field(..., description="ID of the integration")
    service: str = Field(..., description="Name of the integration service")
    api_key: str = Field(..., description="API key for the integration")
    created_at: datetime = Field(..., description="Timestamp of when the integration was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of when the integration was last updated")

    class Config:
        orm_mode = True


class IntegrationListResponse(BaseModel):
    """
    Schema for a list of integration responses.
    """
    items: list[IntegrationResponse] = Field(..., description="List of integration responses")