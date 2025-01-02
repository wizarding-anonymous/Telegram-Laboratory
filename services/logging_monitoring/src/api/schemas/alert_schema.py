from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    """
    Schema for creating a new alert rule.
    """
    metric: str = Field(..., description="Metric to monitor (e.g., cpu_usage, error_rate)")
    threshold: float = Field(..., description="Threshold value for the metric")
    operator: str = Field(..., description="Operator to use for threshold check (>, <, =, >=, <=)")
    notification_channel: str = Field(
        ..., description="Channel for notifications (e.g., email, slack)"
    )
    email: Optional[str] = Field(None, description="Email address for notifications")
    slack_webhook: Optional[str] = Field(None, description="Slack webhook URL for notifications")


class AlertUpdate(BaseModel):
    """
    Schema for updating an existing alert rule.
    """
    metric: Optional[str] = Field(None, description="Updated metric to monitor")
    threshold: Optional[float] = Field(None, description="Updated threshold value")
    operator: Optional[str] = Field(None, description="Updated operator for the threshold check")
    notification_channel: Optional[str] = Field(None, description="Updated notification channel")
    email: Optional[str] = Field(None, description="Updated email address for notifications")
    slack_webhook: Optional[str] = Field(None, description="Updated slack webhook URL for notifications")


class AlertResponse(BaseModel):
    """
    Schema for an alert rule response.
    """
    id: int = Field(..., description="ID of the alert rule")
    metric: str = Field(..., description="Metric to monitor")
    threshold: float = Field(..., description="Threshold value for the metric")
    operator: str = Field(..., description="Operator for threshold check")
    notification_channel: str = Field(..., description="Notification channel")
    email: Optional[str] = Field(None, description="Email address for notifications")
    slack_webhook: Optional[str] = Field(None, description="Slack webhook URL for notifications")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

    class Config:
        orm_mode = True


class AlertListResponse(BaseModel):
    """
    Schema for a list of alert rule responses.
    """
    items: List[AlertResponse]