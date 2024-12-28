from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class WebhookCreate(BaseModel):
    """Schema for creating a new webhook block."""
    url: str


class WebhookUpdate(BaseModel):
    """Schema for updating an existing webhook block."""
    url: str


class WebhookResponse(BaseModel):
    """Schema for a webhook response."""
    id: int
    type: str
    url: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class WebhookListResponse(BaseModel):
    """Schema for a list of webhook responses."""
    items: List[WebhookResponse]