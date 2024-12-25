# services\bot_constructor_service\src\api\schemas\block_schema.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional

from src.core.utils.validators import (
    validate_block_type,
    validate_connections,
    validate_block_ids
)

class BlockCreate(BaseModel):
    """Schema for creating a new block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    type: str = Field(..., description="Type of the block (e.g., 'message', 'action')")
    content: dict = Field(..., description="Content of the block")
    connections: Optional[List[int]] = Field(
        default=[], description="List of IDs of connected blocks"
    )

    @validator("type")
    def validate_type(cls, value):
        # Используем функцию из validators.py для валидации типа блока
        return validate_block_type(value)

    @validator("connections")
    def validate_connections_field(cls, value):
        # Используем функцию из validators.py для валидации списка соединений
        return validate_connections(value)

class BlockUpdate(BaseModel):
    """Schema for updating an existing block."""
    type: Optional[str] = Field(None, description="Updated type of the block")
    content: Optional[dict] = Field(None, description="Updated content of the block")
    connections: Optional[List[int]] = Field(
        None, description="Updated list of IDs of connected blocks"
    )

    @validator("type")
    def validate_type(cls, value):
        if value:
            # Используем функцию из validators.py для валидации типа блока
            return validate_block_type(value)
        return value

class BlockResponse(BaseModel):
    """Schema for returning block data in responses."""
    id: int = Field(..., description="ID of the block")
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    type: str = Field(..., description="Type of the block")
    content: dict = Field(..., description="Content of the block")
    connections: List[int] = Field(..., description="List of IDs of connected blocks")
    created_at: str = Field(..., description="Timestamp when the block was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the block was last updated")

    class Config:
        orm_mode = True

class BlockConnection(BaseModel):
    """Schema for creating a connection between blocks."""
    source_block_id: int = Field(..., description="ID of the source block")
    target_block_id: int = Field(..., description="ID of the target block")

    @validator("source_block_id", "target_block_id")
    def validate_block_ids_field(cls, value):
        # Используем функцию из validators.py для валидации ID блока
        return validate_block_ids([value])[0]  # Возвращаем первый элемент из списка
