from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class BotCreate(BaseModel):
    """
    Schema for creating a new bot.
    """
    name: str = Field(..., description="Name of the bot")
    description: Optional[str] = Field(None, description="Description of the bot")
    user_id: int = Field(..., description="User ID of the bot's owner")


class BotUpdate(BaseModel):
    """
    Schema for updating an existing bot.
    """
    name: Optional[str] = Field(None, description="Updated name of the bot")
    description: Optional[str] = Field(None, description="Updated description of the bot")


class BotResponse(BaseModel):
    """
    Schema for bot response.
    """
    id: int = Field(..., description="Bot ID")
    name: str = Field(..., description="Name of the bot")
    description: Optional[str] = Field(None, description="Description of the bot")
    user_id: int = Field(..., description="User ID of the bot's owner")
    created_at: datetime = Field(..., description="Date and time of creation")
    dsn: Optional[str] = Field(None, description="Connection string of the bot's database")


class BotListResponse(BaseModel):
    """
    Schema for a list of bots responses.
    """
    items: List[BotResponse]