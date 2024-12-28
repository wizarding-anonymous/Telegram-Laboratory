from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class DatabaseConnect(BaseModel):
    """Schema for creating a database connection block."""
    connection_params: Optional[Dict[str, Any]] = None


class DatabaseQuery(BaseModel):
    """Schema for executing a database query."""
    query: str


class DatabaseResponse(BaseModel):
    """Schema for a database block response."""
    id: int
    type: str
    db_uri: Optional[str] = None
    query: Optional[str] = None
    connection_params: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class DatabaseListResponse(BaseModel):
    """Schema for a list of database responses."""
    items: List[DatabaseResponse]