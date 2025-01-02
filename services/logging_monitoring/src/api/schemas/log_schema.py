from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    """
    Schema for creating a new log entry.
    """
    level: str = Field(..., description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    service: str = Field(..., description="Name of the service that generated the log")
    message: str = Field(..., description="Log message")
    timestamp: Optional[str] = Field(None, description="Timestamp of the log")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the log entry")

class LogResponse(BaseModel):
    """
    Schema for a log entry response.
    """
    id: int = Field(..., description="ID of the log entry")
    level: str = Field(..., description="Log level")
    service: str = Field(..., description="Service that generated the log")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(..., description="Timestamp of the log")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the log entry")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        orm_mode = True
        

class LogListResponse(BaseModel):
    """
    Schema for a list of log entries.
    """
    items: List[LogResponse] = Field(..., description="List of log entries")