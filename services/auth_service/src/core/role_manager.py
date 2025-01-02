from typing import List, Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from loguru import logger

from src.db.repositories import RoleRepository
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.core.utils.exceptions import ValidationException

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class RoleManager:
    """
    Manages role-related business logic.
    """
    def __init__(self,
                 role_repository: RoleRepository = Depends(),
                 session: AsyncSession = Depends(get_session),
                 ):
        self.role_repository = role_repository
        self.session = session

    @handle_exceptions
    async def create_role(self, name: str, permissions: List[str]) -> Dict[str, Any]:
        """Creates a new role."""
        logging_client.info(f"Creating new role with name: {name}")

        if not name or not permissions:
           logging_client.warning("Role name or permission cannot be empty.")
           raise ValidationException("Role name and permission are required.")

        try:
           role = await self.role_repository.create(name=name, permissions=permissions)
           logging_client.info(f"Role with name {name} created successfully")
           return role.__dict__
        except Exception as e:
           logging_client.error(f"Error creating role with name: {name}. Error: {e}")
           raise

    @handle_exceptions
    async def get_role(self, role_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a role by its ID."""
        logging_client.info(f"Getting role with ID: {role_id}")
        try:
            role = await self.role_repository.get(role_id=role_id)
            if not role:
                 logging_client.warning(f"Role with ID {role_id} not found")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
                 )
            logging_client.info(f"Role with ID {role_id} retrieved successfully.")
            return role.__dict__
        except Exception as e:
            logging_client.error(f"Error getting role {role_id}: {e}")
            raise

    @handle_exceptions
    async def get_all_roles(self) -> List[Dict[str, Any]]:
        """Retrieves all roles."""
        logging_client.info("Getting all roles")
        try:
           roles = await self.role_repository.get_all()
           logging_client.info(f"Successfully retrieved {len(roles)} roles.")
           return [role.__dict__ for role in roles]
        except Exception as e:
            logging_client.error(f"Error getting all roles: {e}")
            raise

    @handle_exceptions
    async def update_role(
        self, role_id: int, name: Optional[str] = None, permissions: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing role."""
        logging_client.info(f"Updating role with ID: {role_id}")
        try:
            role = await self.role_repository.update(
                role_id=role_id, name=name, permissions=permissions
            )
            if not role:
               logging_client.warning(f"Role with ID {role_id} not found")
               raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
               )
            logging_client.info(f"Role with ID {role_id} updated successfully.")
            return role.__dict__
        except Exception as e:
             logging_client.error(f"Error updating role {role_id}: {e}")
             raise

    @handle_exceptions
    async def delete_role(self, role_id: int) -> Optional[Dict[str, Any]]:
        """Deletes a role by its ID."""
        logging_client.info(f"Deleting role with ID: {role_id}")
        try:
            role = await self.role_repository.delete(role_id=role_id)
            if not role:
                logging_client.warning(f"Role with ID {role_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
                )
            logging_client.info(f"Role with id: {role_id} deleted successfully")
            return role.__dict__
        except Exception as e:
            logging_client.error(f"Error deleting role {role_id}: {e}")
            raise