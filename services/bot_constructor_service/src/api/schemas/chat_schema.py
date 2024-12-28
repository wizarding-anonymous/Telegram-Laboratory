from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ChatMemberCreate(BaseModel):
    """Schema for creating a new chat member block."""
    chat_id: int
    user_id: int


class ChatMemberResponse(BaseModel):
    """Schema for a chat member block response."""
    id: int
    type: str
    chat_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ChatMemberListResponse(BaseModel):
    """Schema for a list of chat member block responses."""
    items: List[ChatMemberResponse]


class ChatTitleUpdate(BaseModel):
    """Schema for updating a chat title."""
    chat_id: int
    title: str


class ChatDescriptionUpdate(BaseModel):
    """Schema for updating a chat description."""
    chat_id: int
    description: str


class ChatMessagePinUpdate(BaseModel):
    """Schema for pinning a message in chat."""
    chat_id: int
    message_id: int


class ChatMessageUnpinUpdate(BaseModel):
    """Schema for unpinning a message in chat."""
    chat_id: int
    message_id: int