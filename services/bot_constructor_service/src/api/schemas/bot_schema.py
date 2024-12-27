from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BotBase(BaseModel):
    """Base schema for bot."""
    name: str = Field(..., min_length=3, max_length=255, description="Name of the bot")
    description: Optional[str] = Field(
        None, max_length=1000, description="Description of the bot"
    )
    status: Optional[str] = Field(
        "draft", description="Status of the bot (draft, active, inactive)"
    )
    version: Optional[str] = Field("1.0.0", description="Version of the bot")


class BotCreate(BotBase):
    """Schema for creating a new bot."""
    template_id: Optional[int] = Field(None, description="ID of the template to use")


class BotUpdate(BotBase):
    """Schema for updating an existing bot."""
    pass


class BotResponse(BotBase):
    """Schema for bot response."""
    id: int = Field(..., description="ID of the bot")
    user_id: int = Field(..., description="User ID of the bot owner")
    created_at: datetime = Field(..., description="Creation timestamp")
    logic: Optional[dict] = Field(None, description="Bot logic data")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")


class BotListResponse(BaseModel):
    """Schema for a single bot in list response"""
    id: int = Field(..., description="ID of the bot")
    name: str = Field(..., description="Name of the bot")
    description: Optional[str] = Field(None, description="Description of the bot")
    created_at: datetime = Field(..., description="Creation timestamp")


class BotWithLogicResponse(BotResponse):
    """Schema for bot response including logic."""
    logic: Optional[dict] = Field(
        None, description="Logic configuration of the bot"
    )