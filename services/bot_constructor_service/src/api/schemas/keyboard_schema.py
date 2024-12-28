# src/api/schemas/keyboard_schema.py

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class KeyboardButtonSchema(BaseModel):
    """Schema for a keyboard button."""
    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None
    
class ReplyKeyboardCreate(BaseModel):
    """Schema for creating a new reply keyboard block."""
    buttons: List[KeyboardButtonSchema]

class ReplyKeyboardUpdate(BaseModel):
    """Schema for updating an existing reply keyboard block."""
    buttons: List[KeyboardButtonSchema]

class ReplyKeyboardResponse(BaseModel):
    """Schema for a reply keyboard response."""
    id: int
    type: str
    buttons: List[KeyboardButtonSchema]
    created_at: datetime
    updated_at: Optional[datetime] = None

class ReplyKeyboardListResponse(BaseModel):
    """Schema for a list of reply keyboard responses."""
    items: List[ReplyKeyboardResponse]


class InlineKeyboardCreate(BaseModel):
    """Schema for creating a new inline keyboard block."""
    buttons: List[KeyboardButtonSchema]


class InlineKeyboardUpdate(BaseModel):
    """Schema for updating an existing inline keyboard block."""
    buttons: List[KeyboardButtonSchema]

class InlineKeyboardResponse(BaseModel):
    """Schema for an inline keyboard response."""
    id: int
    type: str
    buttons: List[KeyboardButtonSchema]
    created_at: datetime
    updated_at: Optional[datetime] = None

class InlineKeyboardListResponse(BaseModel):
    """Schema for a list of inline keyboard responses."""
    items: List[InlineKeyboardResponse]