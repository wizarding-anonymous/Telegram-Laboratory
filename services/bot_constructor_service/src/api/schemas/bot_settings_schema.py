from typing import Optional
from pydantic import BaseModel, Field


class BotSettingsCreate(BaseModel):
    """
    Schema for creating bot settings.
    """
    token: str = Field(..., description="Telegram bot token")
    library: str = Field(
        ..., description="Telegram bot library (telegram_api, aiogram, telebot)"
    )


class BotSettingsUpdate(BaseModel):
    """
    Schema for updating bot settings.
    """
    token: Optional[str] = Field(None, description="Telegram bot token")
    library: Optional[str] = Field(
        None, description="Telegram bot library (telegram_api, aiogram, telebot)"
    )


class BotSettingsResponse(BaseModel):
    """
    Schema for bot settings response.
    """
    id: int = Field(..., description="Bot ID")
    token: str = Field(..., description="Telegram bot token")
    library: str = Field(
        ..., description="Telegram bot library (telegram_api, aiogram, telebot)"
    )

    class Config:
        orm_mode = True