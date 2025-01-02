from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MetadataCreate(BaseModel):
    """
    Schema for creating new metadata.
    """
    bot_id: int = Field(..., description="ID of the bot associated with this metadata")
    key: str = Field(..., description="Key of the metadata")
    value: str = Field(..., description="Value of the metadata")


class MetadataUpdate(BaseModel):
    """
    Schema for updating existing metadata.
    """
    key: Optional[str] = Field(None, description="Updated key of the metadata")
    value: Optional[str] = Field(None, description="Updated value of the metadata")


class MetadataResponse(BaseModel):
    """
    Schema for metadata response.
    """
    id: int = Field(..., description="Metadata ID")
    bot_id: int = Field(..., description="ID of the associated bot")
    key: str = Field(..., description="Key of the metadata")
    value: str = Field(..., description="Value of the metadata")
    created_at: datetime = Field(..., description="Date and time of creation")

    class Config:
        orm_mode = True