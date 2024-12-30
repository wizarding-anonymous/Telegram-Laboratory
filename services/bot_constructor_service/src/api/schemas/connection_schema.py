from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ConnectionCreate(BaseModel):
    """Schema for creating a new connection between blocks."""
    source_block_id: int = Field(..., description="ID of the source block")
    target_block_id: int = Field(..., description="ID of the target block")
    type: Optional[str] = Field("default", description="Type of the connection")


class ConnectionUpdate(BaseModel):
    """Schema for updating an existing connection between blocks."""
    source_block_id: Optional[int] = Field(None, description="ID of the source block")
    target_block_id: Optional[int] = Field(None, description="ID of the target block")
    type: Optional[str] = Field(None, description="Type of the connection")


class ConnectionResponse(BaseModel):
    """Schema for a connection response."""
    id: int = Field(..., description="Connection ID")
    source_block_id: int = Field(..., description="ID of the source block")
    target_block_id: int = Field(..., description="ID of the target block")
    type: Optional[str] = Field(None, description="Type of the connection")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

    class Config:
        orm_mode = True


class ConnectionListResponse(BaseModel):
    """Schema for a list of connection responses."""
    items: List[ConnectionResponse]