from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """
    Schema for a single notification response.
    """
    id: int = Field(..., description="ID of the notification")
    type: str = Field(..., description="Type of the notification (e.g., 'error', 'info', 'warning')")
    message: str = Field(..., description="Message of the notification")
    timestamp: datetime = Field(..., description="Timestamp of when the notification was created")
    status: str = Field(..., description="Status of the notification (e.g., 'unread', 'read', 'archived')")
    created_at: datetime = Field(..., description="Date and time when the notification was created")
    updated_at: Optional[datetime] = Field(None, description="Date and time when the notification was last updated")
    
    class Config:
        orm_mode = True


class NotificationListResponse(BaseModel):
    """
    Schema for a list of notification responses.
    """
    items: list[NotificationResponse] = Field(..., description="List of notification responses")

class NotificationUpdate(BaseModel):
    """
    Schema for updating notification status
    """
    status: str = Field(..., description="Updated status of the notification")