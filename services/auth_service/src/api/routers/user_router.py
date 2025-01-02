from fastapi import APIRouter, Depends, status

from src.api.controllers import UserController
from src.api.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
    SuccessResponse,
    ErrorResponse
)
from src.api.middleware.auth import AuthMiddleware, admin_required

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def create_user(
    user_data: UserCreate, controller: UserController = Depends()
) -> UserResponse:
    """
    Creates a new user in the system.
    """
    return await controller.create_user(user_data=user_data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by their ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def get_user(
    user_id: int, controller: UserController = Depends()
) -> UserResponse:
    """
    Retrieves a user from the system using the provided user ID.
    """
    return await controller.get_user(user_id=user_id)


@router.get(
    "",
    response_model=UserListResponse,
    summary="Get all users",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def get_all_users(controller: UserController = Depends()) -> UserListResponse:
    """
    Retrieves a list of all users in the system.
    """
    return await controller.get_all_users()


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update an existing user",
     dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def update_user(
    user_id: int, user_data: UserUpdate, controller: UserController = Depends()
) -> UserResponse:
    """
    Updates the details of an existing user in the system.
    """
    return await controller.update_user(user_id=user_id, user_data=user_data)


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="Delete a user by their ID",
     dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def delete_user(
    user_id: int, controller: UserController = Depends()
) -> SuccessResponse:
    """
    Deletes a user from the system using the provided user ID.
    """
    return await controller.delete_user(user_id=user_id)

@router.post(
    "/{user_id}/block",
    response_model=SuccessResponse,
    summary="Block a user by their ID",
     dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def block_user(
    user_id: int, controller: UserController = Depends()
) -> SuccessResponse:
    """
    Blocks a user by its ID.
    """
    return await controller.block_user(user_id=user_id)

@router.post(
    "/{user_id}/unblock",
    response_model=SuccessResponse,
    summary="Unblock a user by their ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def unblock_user(
    user_id: int, controller: UserController = Depends()
) -> SuccessResponse:
    """
    Unblocks a user by its ID.
    """
    return await controller.unblock_user(user_id=user_id)