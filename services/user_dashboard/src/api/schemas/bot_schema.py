from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AnalyticsResponse(BaseModel):
    """
    Schema for a single bot's analytics data.
    """
    total_messages: int = Field(..., description="Total number of messages processed by the bot")
    active_users: int = Field(..., description="Number of active users interacting with the bot")
    error_count: int = Field(..., description="Number of errors encountered by the bot")
    created_at: datetime = Field(..., description="Date and time when analytics data was generated")
    updated_at: Optional[datetime] = Field(None, description="Date and time when analytics data was last updated")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata related to bot analytics")


class AnalyticsOverviewResponse(BaseModel):
     """
    Schema for an overview of analytics data for all bots of the current user.
    """
     total_messages: int = Field(..., description="Total number of messages processed by all bots")
     total_active_users: int = Field(..., description="Total number of active users interacting with all bots")
     total_error_count: int = Field(..., description="Total number of errors encountered by all bots")
     metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata related to overview analytics")