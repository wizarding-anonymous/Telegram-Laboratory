# user_dashboard/src/schemas/user_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Jane Doe")
    email: Optional[EmailStr] = Field(None, example="jane.doe@example.com")

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
