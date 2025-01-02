from typing import List

from fastapi import APIRouter, Depends, status

from src.api.controllers import RoleController
from src.api.schemas import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    RoleListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware, admin_required

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def create_role(
    role_data: RoleCreate, controller: RoleController = Depends()
) -> RoleResponse:
    """
    Creates a new role with the given data.
    """
    return await controller.create_role(role_data=role_data)


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get a role by its ID",
     dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def get_role(
    role_id: int, controller: RoleController = Depends()
) -> RoleResponse:
    """
    Retrieves a role by its unique ID.
    """
    return await controller.get_role(role_id=role_id)


@router.get(
    "",
    response_model=RoleListResponse,
    summary="Get a list of all roles",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def get_all_roles(controller: RoleController = Depends()) -> RoleListResponse:
    """
    Retrieves a list of all roles in the system.
    """
    return await controller.get_all_roles()


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update an existing role",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def update_role(
    role_id: int, role_data: RoleUpdate, controller: RoleController = Depends()
) -> RoleResponse:
    """
    Updates an existing role by its ID with new data.
    """
    return await controller.update_role(role_id=role_id, role_data=role_data)


@router.delete(
    "/{role_id}",
    response_model=SuccessResponse,
    summary="Delete a role by its ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def delete_role(
    role_id: int, controller: RoleController = Depends()
) -> SuccessResponse:
    """
    Deletes a role from the system by its ID.
    """
    return await controller.delete_role(role_id=role_id)