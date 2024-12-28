from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel


class VariableCreate(BaseModel):
    """Schema for creating a new variable block."""
    name: str
    value: Optional[Any] = None


class VariableUpdate(BaseModel):
    """Schema for updating an existing variable block."""
    name: str
    value: Optional[Any] = None


class VariableResponse(BaseModel):
    """Schema for a variable block response."""
    id: int
    type: str
    name: str
    value: Optional[Any]
    created_at: datetime
    updated_at: Optional[datetime] = None


class VariableListResponse(BaseModel):
    """Schema for a list of variable responses."""
    items: List[VariableResponse]