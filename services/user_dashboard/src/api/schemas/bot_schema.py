# user_dashboard/src/schemas/bot_schema.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BotBase(BaseModel):
    """
    Базовая модель данных для бота.
    """
    name: str = Field(..., title="Bot Name", max_length=255, description="Название бота")
    description: Optional[str] = Field(None, title="Bot Description", description="Описание бота")

class BotCreateRequest(BotBase):
    """
    Модель данных для создания нового бота.
    """
    pass

class BotUpdateRequest(BaseModel):
    """
    Модель данных для обновления информации о боте.
    """
    name: Optional[str] = Field(None, title="Bot Name", max_length=255, description="Название бота")
    description: Optional[str] = Field(None, title="Bot Description", description="Описание бота")

class BotResponse(BotBase):
    """
    Модель ответа для отображения информации о боте.
    """
    id: int = Field(..., title="Bot ID", description="Уникальный идентификатор бота")
    created_at: datetime = Field(..., title="Created At", description="Дата и время создания бота")

    class Config:
        orm_mode = True
