# services\auth_service\src\api\routers\roles_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.api.middleware.auth_middleware import check_permissions, admin_required
from src.core.utils.security import PermissionType, verify_and_decode_token
from src.api.controllers.roles_controller import RolesController
from src.api.schemas.request_schema import RoleCreateRequest, RoleUpdateRequest
from src.api.schemas.response_schema import MessageResponse, RoleResponse
from loguru import logger

router = APIRouter(prefix="/roles", tags=["Roles"])


async def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            logger.warning("Invalid authorization scheme")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme. Use Bearer"
            )

        payload, is_valid = verify_and_decode_token(token, expected_type="access")
        if not is_valid:
            logger.warning("Invalid or expired token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return payload
    except ValueError:
        logger.warning("Invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use 'Bearer <token>'"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


@router.get(
    "",
    response_model=List[RoleResponse],
    dependencies=[Depends(verify_token), Depends(check_permissions(PermissionType.READ_ROLES.value))]
)
async def get_roles(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        controller = RolesController(session)
        roles = await controller.get_roles(authorization)
        return roles
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve roles"
        )


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(verify_token), Depends(check_permissions(PermissionType.READ_ROLES.value))]
)
async def get_role_by_id(
    role_id: int,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        controller = RolesController(session)
        role = await controller.get_role_by_id(role_id, authorization)
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role"
        )


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_token), Depends(check_permissions(PermissionType.CREATE_ROLES.value))]
)
async def create_role(
    role_data: RoleCreateRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        controller = RolesController(session)
        await controller.create_role(role_data, authorization)
        return MessageResponse(message="Role created successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role"
        )


@router.put(
    "/{role_id}",
    response_model=MessageResponse,
    dependencies=[Depends(verify_token), Depends(check_permissions(PermissionType.UPDATE_ROLES.value))]
)
async def update_role(
    role_id: int,
    role_data: RoleUpdateRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        controller = RolesController(session)
        await controller.update_role(role_id, role_data, authorization)
        return MessageResponse(message="Role updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )


@router.delete(
    "/{role_id}",
    response_model=MessageResponse,
    dependencies=[Depends(verify_token), Depends(check_permissions(PermissionType.DELETE_ROLES.value))]
)
async def delete_role(
    role_id: int,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        controller = RolesController(session)
        await controller.delete_role(role_id, authorization)
        return MessageResponse(message="Role deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role"
        )
