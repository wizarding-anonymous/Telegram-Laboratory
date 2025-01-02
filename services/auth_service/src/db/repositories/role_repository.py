from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Role
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class RoleRepository:
    """
    Repository for performing CRUD operations on the Role model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, name: str, permissions: List[str]) -> Role:
        """
        Creates a new role in the database.
        """
        logger.info(f"Creating role with name: {name}")
        try:
            role = Role(name=name, permissions=permissions)
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
            logger.info(f"Role created successfully with id: {role.id}")
            return role
        except Exception as e:
             logger.error(f"Error creating role with name {name}: {e}")
             raise DatabaseException(f"Failed to create role: {e}") from e


    @handle_exceptions
    async def get(self, role_id: int) -> Optional[Role]:
        """
        Retrieves a role by its ID.
        """
        logger.info(f"Getting role with ID: {role_id}")
        try:
            query = select(Role).where(Role.id == role_id)
            result = await self.session.execute(query)
            role = result.scalar_one_or_none()
            if role:
                logger.debug(f"Role with ID {role_id} found")
            else:
                logger.warning(f"Role with ID {role_id} not found")
            return role
        except Exception as e:
            logger.error(f"Error getting role {role_id}: {e}")
            raise DatabaseException(f"Failed to get role with id {role_id}: {e}") from e

    @handle_exceptions
    async def get_all(self) -> List[Role]:
        """
        Retrieves all roles.
        """
        logger.info("Getting all roles")
        try:
            query = select(Role)
            result = await self.session.execute(query)
            roles = list(result.scalars().all())
            logger.debug(f"Found {len(roles)} roles")
            return roles
        except Exception as e:
            logger.error(f"Error getting all roles: {e}")
            raise DatabaseException(f"Failed to get all roles: {e}") from e

    @handle_exceptions
    async def update(self, role_id: int, name: Optional[str] = None, permissions: Optional[List[str]] = None) -> Optional[Role]:
        """
        Updates an existing role by its ID.
        """
        logger.info(f"Updating role with ID: {role_id}, name: {name}, permissions: {permissions}")
        try:
            query = select(Role).where(Role.id == role_id)
            result = await self.session.execute(query)
            role = result.scalar_one_or_none()
            if role:
                if name is not None:
                     role.name = name
                if permissions is not None:
                     role.permissions = permissions
                await self.session.commit()
                await self.session.refresh(role)
                logger.info(f"Role with ID {role_id} updated successfully.")
            else:
                logger.warning(f"Role with ID {role_id} not found for update.")
            return role
        except Exception as e:
           logger.error(f"Error updating role with ID {role_id}: {e}")
           raise DatabaseException(f"Failed to update role with id {role_id}: {e}") from e


    @handle_exceptions
    async def delete(self, role_id: int) -> Optional[Role]:
         """
         Deletes a role by its ID.
         """
         logger.info(f"Deleting role with ID: {role_id}")
         try:
            query = delete(Role).where(Role.id == role_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Role with ID {role_id} deleted successfully.")
            return result.scalar_one_or_none()
         except Exception as e:
            logger.error(f"Error deleting role with ID {role_id}: {e}")
            raise DatabaseException(f"Failed to delete role with id {role_id}: {e}") from e