from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RouteCreate(BaseModel):
    """
    Schema for creating a new route.
    """
    path: str = Field(..., description="Path for the route (e.g. /api/v1/users)")
    method: str = Field(..., description="HTTP method for the route (e.g. GET, POST)")
    destination_url: str = Field(..., description="Destination URL for the route")
    auth_required: bool = Field(False, description="Is authentication required for this route?")


class RouteUpdate(BaseModel):
    """
    Schema for updating an existing route.
    """
    path: Optional[str] = Field(None, description="Path for the route")
    method: Optional[str] = Field(None, description="HTTP method for the route")
    destination_url: Optional[str] = Field(None, description="Destination URL for the route")
    auth_required: Optional[bool] = Field(None, description="Is authentication required for this route?")


class RouteResponse(BaseModel):
    """
    Schema for the response of a route.
    """
    id: int = Field(..., description="Route ID")
    path: str = Field(..., description="Path for the route (e.g. /api/v1/users)")
    method: str = Field(..., description="HTTP method for the route (e.g. GET, POST)")
    destination_url: str = Field(..., description="Destination URL for the route")
    auth_required: bool = Field(False, description="Is authentication required for this route?")

    class Config:
        orm_mode = True


class RouteListResponse(BaseModel):
    """
    Schema for a list of route responses.
    """
    items: List[RouteResponse]