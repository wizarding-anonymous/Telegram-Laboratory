from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class CallbackQueryCreate(BaseModel):
    """Schema for creating a new callback query handler block."""
    data: str


class CallbackQueryUpdate(BaseModel):
    """Schema for updating an existing callback query handler block."""
    data: str


class CallbackQueryResponse(BaseModel):
    """Schema for a callback query handler response."""
    id: int
    type: str
    data: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class CallbackQueryListResponse(BaseModel):
    """Schema for a list of callback query handler responses."""
    items: List[CallbackQueryResponse]


class CallbackResponseCreate(BaseModel):
    """Schema for creating a new callback response block."""
    text: str


class CallbackResponseUpdate(BaseModel):
    """Schema for updating an existing callback response block."""
    text: str


class CallbackResponseResponse(BaseModel):
    """Schema for a callback response block."""
    id: int
    type: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class CallbackResponseListResponse(BaseModel):
    """Schema for a list of callback response blocks."""
    items: List[CallbackResponseResponse]