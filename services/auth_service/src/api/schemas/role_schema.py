from typing import List, Optional
from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    """
    Schema for creating a new role.
    """
    name: str = Field(..., description="Name of the role")
    permissions: List[str] = Field(..., description="List of permissions for the role")


class RoleUpdate(BaseModel):
    """
    Schema for updating an existing role.
    """
    name: Optional[str] = Field(None, description="Updated name of the role")
    permissions: Optional[List[str]] = Field(None, description="Updated list of permissions for the role")


class RoleResponse(BaseModel):
    """
    Schema for a role response.
    """
    id: int = Field(..., description="ID of the role")
    name: str = Field(..., description="Name of the role")
    permissions: List[str] = Field(..., description="List of permissions for the role")

    class Config:
        orm_mode = True


class RoleListResponse(BaseModel):
    """
    Schema for a list of role responses.
    """
    items: List[RoleResponse]