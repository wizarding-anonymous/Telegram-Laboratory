from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SchemaResponse(BaseModel):
    """
    Schema for a database schema response (DSN).
    """
    id: int = Field(..., description="Schema ID")
    bot_id: int = Field(..., description="ID of the associated bot")
    dsn: str = Field(..., description="Database connection string (DSN)")
    created_at: datetime = Field(..., description="Date and time of creation")

    class Config:
        orm_mode = True