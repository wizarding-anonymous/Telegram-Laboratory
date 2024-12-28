from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class FlowChartCreate(BaseModel):
    """Schema for creating a new flow chart block."""
    logic: Dict[str, Any]


class FlowChartUpdate(BaseModel):
    """Schema for updating an existing flow chart block."""
    logic: Dict[str, Any]


class FlowChartResponse(BaseModel):
    """Schema for a flow chart block response."""
    id: int
    type: str
    logic: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None