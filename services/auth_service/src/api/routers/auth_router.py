from fastapi import APIRouter, Depends, status

from src.api.controllers import AuthController
from src.api.schemas import (
    AuthLogin,
    AuthResponse,
    AuthRegister,
    AuthRefresh,
    SuccessResponse,
    ErrorResponse
)
from src.api.middleware.auth import AuthMiddleware


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


@router.post(
    "/register",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    user_data: AuthRegister, controller: AuthController = Depends()
) -> SuccessResponse:
    """
    Registers a new user in the system.
    """
    return await controller.register_user(user_data=user_data)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate a user and return access and refresh tokens",
)
async def login_user(
    login_data: AuthLogin, controller: AuthController = Depends()
) -> AuthResponse:
    """
    Authenticates a user and returns a JWT access token and a refresh token.
    """
    return await controller.login_user(login_data=login_data)


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="Logs out a user by invalidating the refresh token",
    dependencies=[Depends(AuthMiddleware())]
)
async def logout_user(
    token_data: AuthRefresh, controller: AuthController = Depends()
) -> SuccessResponse:
    """
    Logs out a user by invalidating the provided refresh token.
    """
    return await controller.logout_user(token_data=token_data)


@router.get(
    "/me",
    response_model=Optional[dict],
    summary="Get the current user by token",
    dependencies=[Depends(AuthMiddleware())],
)
async def get_current_user(
    controller: AuthController = Depends(),
    user: dict = Depends(AuthMiddleware())
) -> Optional[dict]:
    """
    Retrieves the current user based on the provided access token.
    """
    return user

@router.post(
    "/refresh",
     response_model=AuthResponse,
    summary="Refresh access token",
    dependencies=[Depends(AuthMiddleware())]
)
async def refresh_token(
    token_data: AuthRefresh, controller: AuthController = Depends()
) -> AuthResponse:
    """
    Refreshes the access token using a valid refresh token.
    """
    return await controller.refresh_token(token_data=token_data)