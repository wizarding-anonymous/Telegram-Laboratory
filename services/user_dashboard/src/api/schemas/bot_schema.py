# user_dashboard/src/schemas/bot_schema.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BotCreate(BaseModel):
    name: str = Field(..., example="MyAwesomeBot")
    description: Optional[str] = Field(None, example="This bot does amazing things!")

class BotUpdate(BaseModel):
    name: Optional[str] = Field(None, example="UpdatedBotName")
    description: Optional[str] = Field(None, example="Updated description of the bot.")

class BotResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
