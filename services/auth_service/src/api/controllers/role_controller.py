from typing import List

from fastapi import Depends, HTTPException, status
from loguru import logger

from src.core.role_manager import RoleManager
from src.api.schemas import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    RoleListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.api.middleware.auth import admin_required
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class RoleController:
    """
    Controller for handling role-related operations.
    """

    def __init__(self, role_manager: RoleManager = Depends()):
        self.role_manager = role_manager

    @handle_exceptions
    async def create_role(self, role_data: RoleCreate, user: dict = Depends(admin_required)) -> RoleResponse:
        """
        Creates a new role.
        """
        logging_client.info(f"Creating new role with data: {role_data.name}")
        try:
            role = await self.role_manager.create_role(
                name=role_data.name, permissions=role_data.permissions
            )
            logging_client.info(f"Role created successfully: {role.name}")
            return RoleResponse(**role.__dict__)
        except Exception as e:
            logging_client.error(f"Failed to create role: {e}")
            raise

    @handle_exceptions
    async def get_role(self, role_id: int, user: dict = Depends(admin_required)) -> RoleResponse:
        """
        Retrieves a role by its ID.
        """
        logging_client.info(f"Getting role with ID: {role_id}")
        try:
            role = await self.role_manager.get_role(role_id=role_id)
            if not role:
                 logging_client.warning(f"Role with ID {role_id} not found")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
                )
            logging_client.info(f"Role retrieved successfully: {role.name}")
            return RoleResponse(**role.__dict__)
        except Exception as e:
             logging_client.error(f"Failed to get role {role_id}: {e}")
             raise

    @handle_exceptions
    async def get_all_roles(self, user: dict = Depends(admin_required)) -> RoleListResponse:
        """
        Retrieves a list of all roles.
        """
        logging_client.info("Getting all roles")
        try:
            roles = await self.role_manager.get_all_roles()
            logging_client.info(f"Successfully retrieved {len(roles)} roles.")
            return RoleListResponse(items=[RoleResponse(**role.__dict__) for role in roles])
        except Exception as e:
             logging_client.error(f"Failed to get all roles: {e}")
             raise

    @handle_exceptions
    async def update_role(self, role_id: int, role_data: RoleUpdate, user: dict = Depends(admin_required)) -> RoleResponse:
        """
        Updates an existing role.
        """
        logging_client.info(f"Updating role with ID: {role_id}")
        try:
            role = await self.role_manager.update_role(
                role_id=role_id, name=role_data.name, permissions=role_data.permissions
            )
            if not role:
                logging_client.warning(f"Role with ID {role_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
                )
            logging_client.info(f"Role updated successfully: {role.name}")
            return RoleResponse(**role.__dict__)
        except Exception as e:
             logging_client.error(f"Failed to update role {role_id}: {e}")
             raise

    @handle_exceptions
    async def delete_role(self, role_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Deletes a role by its ID.
        """
        logging_client.info(f"Deleting role with ID: {role_id}")
        try:
            role = await self.role_manager.delete_role(role_id=role_id)
            if not role:
                logging_client.warning(f"Role with ID {role_id} not found")
                raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
                )
            logging_client.info(f"Role with ID {role_id} deleted successfully.")
            return SuccessResponse(message="Role deleted successfully")
        except Exception as e:
             logging_client.error(f"Failed to delete role {role_id}: {e}")
             raise