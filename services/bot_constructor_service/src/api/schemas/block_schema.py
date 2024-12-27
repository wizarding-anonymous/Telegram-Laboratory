from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BlockBase(BaseModel):
    """Base schema for a block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    type: str = Field(..., description="Type of the block (e.g., text, photo, keyboard)")
    content: dict = Field(..., description="Content of the block (e.g., text, url, buttons)")


class BlockCreate(BlockBase):
    """Schema for creating a new block."""
    pass


class BlockUpdate(BlockBase):
    """Schema for updating an existing block."""
    pass
    

class BlockResponse(BlockBase):
    """Schema for block response."""
    id: int = Field(..., description="ID of the block")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")


class BlockConnection(BaseModel):
    """Schema for creating connections between blocks."""
    source_block_id: int = Field(..., description="ID of the source block")
    target_block_id: int = Field(..., description="ID of the target block")