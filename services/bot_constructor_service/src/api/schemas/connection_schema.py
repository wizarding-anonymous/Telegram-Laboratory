from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ConnectionCreate(BaseModel):
    """Schema for creating a new connection between blocks."""

    source_block_id: int
    target_block_id: int
    type: Optional[str] = "default"


class ConnectionUpdate(BaseModel):
    """Schema for updating an existing connection between blocks."""

    source_block_id: Optional[int] = None
    target_block_id: Optional[int] = None
    type: Optional[str] = None


class ConnectionResponse(BaseModel):
    """Schema for a connection response."""
    id: int
    source_block_id: int
    target_block_id: int
    type: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ConnectionListResponse(BaseModel):
    """Schema for a list of connection responses."""
    items: List[ConnectionResponse]