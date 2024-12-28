from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class TextMessageCreate(BaseModel):
    """Schema for creating a new text message block."""
    content: str


class TextMessageUpdate(BaseModel):
    """Schema for updating an existing text message block."""
    content: str


class TextMessageResponse(BaseModel):
    """Schema for a text message response."""
    id: int
    type: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class TextMessageListResponse(BaseModel):
    """Schema for a list of text message responses."""
    items: List[TextMessageResponse]