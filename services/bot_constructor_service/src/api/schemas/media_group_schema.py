from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class MediaItemSchema(BaseModel):
    """Schema for an individual media item within a media group."""
    type: str  # e.g., "photo", "video", "document"
    media: str  # URL or file ID of the media
    caption: Optional[str] = None #optional caption for media


class MediaGroupCreate(BaseModel):
    """Schema for creating a new media group block."""
    items: List[MediaItemSchema]


class MediaGroupUpdate(BaseModel):
    """Schema for updating an existing media group block."""
    items: List[MediaItemSchema]



class MediaGroupResponse(BaseModel):
    """Schema for a media group block response."""
    id: int
    type: str
    items: List[MediaItemSchema]
    created_at: datetime
    updated_at: Optional[datetime] = None


class MediaGroupListResponse(BaseModel):
    """Schema for a list of media group responses."""
    items: List[MediaGroupResponse]