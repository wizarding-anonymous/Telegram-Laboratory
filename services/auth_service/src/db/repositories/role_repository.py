# services\auth_service\src\db\repositories\role_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from src.db.models.role_model import Role, RoleType
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List

# Определяем собственные исключения для RoleRepository
class RoleRepositoryError(Exception):
    """Базовое исключение для RoleRepository."""
    pass

class RoleNotFoundError(RoleRepositoryError):
    """Исключение, когда роль не найдена."""
    pass

class RoleCreationError(RoleRepositoryError):
    """Исключение при ошибке создания роли."""
    pass

class RoleUpdateError(RoleRepositoryError):
    """Исключение при ошибке обновления роли."""
    pass

class RoleDeletionError(RoleRepositoryError):
    """Исключение при ошибке удаления роли."""
    pass

class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_roles(self) -> list[Role]:
        """Получение всех ролей."""
        try:
            q = select(Role)
            result = await self.session.execute(q)
            roles = result.scalars().all()
            logger.debug(f"Retrieved {len(roles)} roles from the database.")
            return roles
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving all roles: {str(e)}")
            raise RoleRepositoryError("Failed to retrieve roles") from e
        except Exception as e:
            logger.error(f"Unexpected error while retrieving all roles: {str(e)}")
            raise RoleRepositoryError("An unexpected error occurred while retrieving roles") from e

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Получение роли по названию."""
        try:
            q = select(Role).where(Role.name == name)
            result = await self.session.execute(q)
            role = result.scalar_one_or_none()
            if role:
                logger.debug(f"Retrieved role: {role.name}")
            else:
                logger.debug(f"Role with name '{name}' not found.")
            return role
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving role '{name}': {str(e)}")
            raise RoleRepositoryError("Failed to retrieve role") from e
        except Exception as e:
            logger.error(f"Unexpected error while retrieving role '{name}': {str(e)}")
            raise RoleRepositoryError("An unexpected error occurred while retrieving role") from e

    async def create_role(self, name: str, permissions: list[str]) -> Role:
        """Создание новой роли."""
        role = Role(name=name, permissions=permissions)
        self.session.add(role)
        try:
            await self.session.commit()
            await self.session.refresh(role)
            logger.info(f"Role '{name}' created successfully with permissions: {permissions}")
            return role
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while creating role '{name}': {str(e)}")
            raise RoleCreationError("Failed to create role") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while creating role '{name}': {str(e)}")
            raise RoleCreationError("An unexpected error occurred while creating role") from e

    async def create_if_not_exists(self, name: str, permissions: list[str]) -> Role:
        """
        Создает роль, если она не существует.
        
        Args:
            name: Название роли
            permissions: Список разрешений
            
        Returns:
            Role: Существующая или новая роль
        """
        try:
            existing_role = await self.get_by_name(name)
            if existing_role:
                logger.debug(f"Role '{name}' already exists")
                return existing_role

            return await self.create_role(name, permissions)
        except Exception as e:
            logger.error(f"Error in create_if_not_exists for role '{name}': {str(e)}")
            raise RoleCreationError(f"Failed to create or get role '{name}'") from e

    async def ensure_default_roles(self) -> None:
        """
        Обеспечивает наличие всех предопределенных ролей в базе данных.
        """
        try:
            for role_name in Role.PREDEFINED_ROLES:
                permissions = Role.get_default_permissions(role_name)
                await self.create_if_not_exists(role_name, permissions)
                logger.info(f"Ensured existence of predefined role: {role_name}")
        except Exception as e:
            logger.error(f"Failed to ensure default roles: {str(e)}")
            raise RoleCreationError("Failed to ensure default roles") from e

    async def update_role(self, role_id: int, name: Optional[str] = None, 
                         permissions: Optional[List[str]] = None) -> Role:
        """Обновление роли по ID."""
        try:
            stmt = update(Role).where(Role.id == role_id)
            updates = {}
            if name:
                updates["name"] = name
            if permissions:
                updates["permissions"] = permissions

            if not updates:
                logger.warning("No updates provided for role.")
                raise RoleUpdateError("No updates provided.")

            stmt = stmt.values(**updates).returning(Role)
            result = await self.session.execute(stmt)
            updated_role = result.scalar_one_or_none()

            if not updated_role:
                logger.warning(f"Role with ID {role_id} not found for update.")
                raise RoleNotFoundError(f"Role with ID {role_id} not found.")

            await self.session.commit()
            logger.info(f"Role with ID {role_id} updated successfully.")
            return updated_role

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while updating role ID {role_id}: {str(e)}")
            raise RoleUpdateError("Failed to update role") from e
        except RoleNotFoundError:
            raise
        except RoleUpdateError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while updating role ID {role_id}: {str(e)}")
            raise RoleUpdateError("An unexpected error occurred while updating role") from e

    async def delete_role(self, role_id: int) -> bool:
        """Удаление роли по ID."""
        try:
            # Проверяем, не является ли роль предопределенной
            role = await self.session.get(Role, role_id)
            if role and role.name in Role.get_all_predefined_roles():
                logger.warning(f"Attempted to delete predefined role: {role.name}")
                raise RoleDeletionError("Cannot delete predefined role")

            stmt = delete(Role).where(Role.id == role_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Role with ID {role_id} deleted successfully.")
                return True
            else:
                logger.warning(f"No role found with ID {role_id} to delete.")
                return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while deleting role ID {role_id}: {str(e)}")
            raise RoleDeletionError("Failed to delete role") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while deleting role ID {role_id}: {str(e)}")
            raise RoleDeletionError("An unexpected error occurred while deleting role") from e

    async def check_role_exists(self, name: str) -> bool:
        """
        Проверяет существование роли.
        
        Args:
            name: Название роли
            
        Returns:
            bool: True если роль существует, False иначе
        """
        try:
            role = await self.get_by_name(name)
            return role is not None
        except Exception as e:
            logger.error(f"Error checking role existence for '{name}': {str(e)}")
            return False