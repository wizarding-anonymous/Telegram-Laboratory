# auth_service\src\api\controllers\roles_controller.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.db.repositories.role_repository import (
    RoleRepository,
    RoleNotFoundError,
    RoleCreationError,
    RoleUpdateError,
    RoleDeletionError
)
from src.api.schemas.request_schema import RoleCreateRequest, RoleUpdateRequest
from src.core.utils.security import RoleType, PermissionType, verify_and_decode_token
from loguru import logger
from typing import List, Optional, Any


class RolesController:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_repo = RoleRepository(session)

    async def verify_token_and_permissions(self, token: str, required_permissions: List[str]) -> dict:
        try:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authorization token"
                )

            payload, is_valid = verify_and_decode_token(token, expected_type="access")
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )

            user_permissions = payload.get("permissions", [])
            missing_permissions = [
                perm for perm in required_permissions
                if perm not in user_permissions
            ]

            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                )

            return payload

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )

    async def get_roles(self, authorization: str) -> List[Any]:
        try:
            token = authorization.replace("Bearer ", "") if authorization else None
            await self.verify_token_and_permissions(token, [PermissionType.READ_ROLES.value])

            roles = await self.role_repo.get_all_roles()
            logger.debug(f"Retrieved {len(roles)} roles")
            return roles

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get roles: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve roles"
            )

    async def get_role_by_id(self, role_id: int, authorization: str) -> Any:
        try:
            token = authorization.replace("Bearer ", "") if authorization else None
            await self.verify_token_and_permissions(token, [PermissionType.READ_ROLES.value])

            role = await self.role_repo.get_by_id(role_id)
            if not role:
                logger.warning(f"Role with ID {role_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

            logger.debug(f"Retrieved role: {role.name} (ID: {role_id})")
            return role

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get role {role_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve role"
            )

    async def create_role(self, role_data: RoleCreateRequest, authorization: str) -> None:
        try:
            token = authorization.replace("Bearer ", "") if authorization else None
            await self.verify_token_and_permissions(token, [PermissionType.CREATE_ROLES.value])

            if role_data.name in [role.value for role in RoleType]:
                logger.warning(f"Attempt to create predefined role: {role_data.name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot create predefined role"
                )

            existing = await self.role_repo.get_by_name(role_data.name)
            if existing:
                logger.warning(f"Role with name '{role_data.name}' already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role with this name already exists"
                )

            valid_permissions = {perm.value for perm in PermissionType}
            invalid_permissions = set(role_data.permissions) - valid_permissions
            if invalid_permissions:
                logger.warning(f"Invalid permissions provided: {invalid_permissions}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid permissions: {', '.join(invalid_permissions)}"
                )

            await self.role_repo.create_role(role_data.name, role_data.permissions)
            logger.info(f"Created new role: {role_data.name} with permissions: {role_data.permissions}")

        except HTTPException:
            raise
        except RoleCreationError as e:
            logger.error(f"Failed to create role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create role"
            )
        except Exception as e:
            logger.error(f"Unexpected error creating role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    async def update_role(self, role_id: int, role_data: RoleUpdateRequest, authorization: str) -> None:
        try:
            token = authorization.replace("Bearer ", "") if authorization else None
            await self.verify_token_and_permissions(token, [PermissionType.UPDATE_ROLES.value])

            existing_role = await self.role_repo.get_by_id(role_id)
            if not existing_role:
                logger.warning(f"Role with ID {role_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

            if existing_role.name in [role.value for role in RoleType]:
                logger.warning(f"Attempt to update predefined role: {existing_role.name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot modify predefined role"
                )

            if role_data.permissions:
                valid_permissions = {perm.value for perm in PermissionType}
                invalid_permissions = set(role_data.permissions) - valid_permissions
                if invalid_permissions:
                    logger.warning(f"Invalid permissions provided: {invalid_permissions}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid permissions: {', '.join(invalid_permissions)}"
                    )

            await self.role_repo.update_role(role_id, role_data.name, role_data.permissions)
            logger.info(f"Updated role ID {role_id}: {role_data.model_dump(exclude_unset=True)}")

        except HTTPException:
            raise
        except RoleUpdateError as e:
            logger.error(f"Failed to update role {role_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update role"
            )
        except Exception as e:
            logger.error(f"Unexpected error updating role {role_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    async def delete_role(self, role_id: int, authorization: str) -> None:
        try:
            token = authorization.replace("Bearer ", "") if authorization else None
            await self.verify_token_and_permissions(token, [PermissionType.DELETE_ROLES.value])

            existing_role = await self.role_repo.get_by_id(role_id)
            if not existing_role:
                logger.warning(f"Role with ID {role_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

            if existing_role.name in [role.value for role in RoleType]:
                logger.warning(f"Attempt to delete predefined role: {existing_role.name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete predefined role"
                )

            await self.role_repo.delete_role(role_id)
            logger.info(f"Deleted role ID {role_id}")

        except HTTPException:
            raise
        except RoleDeletionError as e:
            logger.error(f"Failed to delete role {role_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete role"
            )
        except Exception as e:
            logger.error(f"Unexpected error deleting role {role_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )
