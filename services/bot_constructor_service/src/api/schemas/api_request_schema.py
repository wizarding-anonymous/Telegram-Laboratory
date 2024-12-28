from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class ApiRequestCreate(BaseModel):
    """Schema for creating a new API request block."""
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None


class ApiRequestUpdate(BaseModel):
    """Schema for updating an existing API request block."""
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None


class ApiRequestResponse(BaseModel):
    """Schema for an API request block response."""
    id: int
    type: str
    method: str
    url: str
    headers: Optional[Dict[str, str]]
    params: Optional[Dict[str, Any]]
    body: Optional[Any]
    created_at: datetime
    updated_at: Optional[datetime] = None


class ApiRequestListResponse(BaseModel):
    """Schema for a list of API request responses."""
    items: List[ApiRequestResponse]