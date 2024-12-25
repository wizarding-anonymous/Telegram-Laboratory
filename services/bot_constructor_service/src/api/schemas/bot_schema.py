# services\bot_constructor_service\src\api\schemas\bot_schema.py
from pydantic import BaseModel, Field
from typing import Optional, List

class BotCreate(BaseModel):
    """
    Schema for creating a new bot.
    """
    name: str = Field(..., max_length=255, description="The name of the bot.")
    description: Optional[str] = Field(None, max_length=1000, description="A brief description of the bot.")
    template_id: Optional[int] = Field(None, description="The ID of a template to base the bot on.")

class BotUpdate(BaseModel):
    """
    Schema for updating bot information.
    """
    name: Optional[str] = Field(None, max_length=255, description="The new name of the bot.")
    description: Optional[str] = Field(None, max_length=1000, description="Updated description of the bot.")

class BotResponse(BaseModel):
    """
    Schema for returning bot details in responses.
    """
    id: int
    name: str
    description: Optional[str]
    created_at: str

    class Config:
        orm_mode = True

class BotListResponse(BaseModel):
    """
    Schema for returning a list of bots.
    """
    bots: List[BotResponse]
