from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """
    email: str = Field(..., description="Email address of the new user")
    password: str = Field(..., min_length=6, description="Password for the new user")

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    """
    email: Optional[str] = Field(None, description="Updated email address")
    is_active: Optional[bool] = Field(None, description="Updated status of the user")


class UserResponse(BaseModel):
    """
    Schema for a user response.
    """
    id: int = Field(..., description="ID of the user")
    email: str = Field(..., description="Email address of the user")
    is_active: bool = Field(..., description="Status of the user")
    created_at: datetime = Field(..., description="Date and time of creation")
    updated_at: Optional[datetime] = Field(None, description="Date and time of last update")

    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    """
    Schema for a list of user responses.
    """
    items: list[UserResponse] = Field(..., description="List of user responses")