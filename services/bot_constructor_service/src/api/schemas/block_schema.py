from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BlockBase(BaseModel):
    """Base schema for a block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    type: str = Field(..., description="Type of the block (e.g., text_message, photo, keyboard, callback, api_request)")
    content: Optional[Dict[str, Any]] = Field(None, description="Content of the block (e.g., text, url, buttons, logic)")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")
    
class BlockCreate(BlockBase):
    """Schema for creating a new block."""
    pass


class BlockUpdate(BaseModel):
    """Schema for updating an existing block."""
    bot_id: Optional[int] = Field(None, description="ID of the bot this block belongs to")
    type: Optional[str] = Field(None, description="Type of the block (e.g., text_message, photo, keyboard, callback, api_request)")
    content: Optional[Dict[str, Any]] = Field(None, description="Content of the block (e.g., text, url, buttons, logic)")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class BlockResponse(BlockBase):
    """Schema for block response."""
    id: int = Field(..., description="ID of the block")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    user_message_id: Optional[int] = Field(None, description="User message id")
    bot_message_id: Optional[int] = Field(None, description="Bot message id")


class BlockConnection(BaseModel):
    """Schema for creating connections between blocks."""
    source_block_id: int = Field(..., description="ID of the source block")
    target_block_id: int = Field(..., description="ID of the target block")


class TextMessageCreate(BaseModel):
    """Schema for creating a new text message block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    content: str = Field(..., description="Text content of the message")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class TextMessageUpdate(BaseModel):
    """Schema for updating an existing text message block."""
    content: Optional[str] = Field(None, description="Text content of the message")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class TextMessageResponse(BaseModel):
    """Schema for a text message response."""
    id: int = Field(..., description="ID of the block")
    type: str = Field(..., description="Type of the block")
    content: str = Field(..., description="Text content of the message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    user_message_id: Optional[int] = Field(None, description="User message id")
    bot_message_id: Optional[int] = Field(None, description="Bot message id")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class KeyboardCreate(BaseModel):
    """Schema for creating a new keyboard block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    buttons: List[List[str]] = Field(..., description="List of buttons for the keyboard")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class KeyboardUpdate(BaseModel):
    """Schema for updating an existing keyboard block."""
    buttons: Optional[List[List[str]]] = Field(None, description="List of buttons for the keyboard")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class KeyboardResponse(BaseModel):
    """Schema for a keyboard block response."""
    id: int = Field(..., description="ID of the block")
    type: str = Field(..., description="Type of the block")
    buttons: List[List[str]] = Field(..., description="List of buttons for the keyboard")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class CallbackCreate(BaseModel):
    """Schema for creating a new callback block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    callback_data: str = Field(..., description="Callback data")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class CallbackUpdate(BaseModel):
    """Schema for updating an existing callback block."""
    callback_data: Optional[str] = Field(None, description="Callback data")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class CallbackResponse(BaseModel):
    """Schema for a callback block response."""
    id: int = Field(..., description="ID of the block")
    type: str = Field(..., description="Type of the block")
    callback_data: str = Field(..., description="Callback data")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class ApiRequestCreate(BaseModel):
    """Schema for creating a new API request block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    url: str = Field(..., description="URL for API request")
    method: str = Field(..., description="HTTP method for API request")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers for API request")
    params: Optional[Dict[str, str]] = Field(None, description="Query parameters for API request")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class ApiRequestUpdate(BaseModel):
    """Schema for updating an existing API request block."""
    url: Optional[str] = Field(None, description="URL for API request")
    method: Optional[str] = Field(None, description="HTTP method for API request")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers for API request")
    params: Optional[Dict[str, str]] = Field(None, description="Query parameters for API request")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class ApiRequestResponse(BaseModel):
    """Schema for an API request block response."""
    id: int = Field(..., description="ID of the block")
    type: str = Field(..., description="Type of the block")
    url: str = Field(..., description="URL for API request")
    method: str = Field(..., description="HTTP method for API request")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers for API request")
    params: Optional[Dict[str, str]] = Field(None, description="Query parameters for API request")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class WebhookCreate(BaseModel):
    """Schema for creating a new webhook block."""
    bot_id: int = Field(..., description="ID of the bot this block belongs to")
    url: str = Field(..., description="URL for the webhook")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class WebhookUpdate(BaseModel):
    """Schema for updating an existing webhook block."""
    url: Optional[str] = Field(None, description="URL for the webhook")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")


class WebhookResponse(BaseModel):
    """Schema for a webhook block response."""
    id: int = Field(..., description="ID of the block")
    type: str = Field(..., description="Type of the block")
    url: str = Field(..., description="URL for the webhook")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    connections: Optional[List[int]] = Field(None, description="List of connected block IDs")