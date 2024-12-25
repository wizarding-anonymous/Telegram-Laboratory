# services/auth_service/src/api/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from typing import Optional
from src.api.controllers.auth_controller import AuthController
from src.api.schemas.request_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    LogoutRequest,
    TokenRefreshRequest,
    PasswordResetRequest,
    PasswordChangeRequest,
    BulkRoleUpdateRequest
)
from src.api.schemas.response_schema import (
    MessageResponse,
    TokenResponse,
    UserResponse,
    AuthResponse
)
from src.db.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from sqlalchemy.orm import selectinload
from src.db.models.user_model import User
from src.core.utils.security import verify_and_decode_token
from datetime import timezone

router = APIRouter(
    tags=["Authentication"],
    responses={
        400: {"model": MessageResponse, "description": "Bad Request"},
        401: {
            "model": MessageResponse,
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid Authorization header format. Use 'Bearer &lt;token&gt;'",
                        "status_code": 401,
                        "error": "Authentication Error"
                    }
                }
            }
        },
        403: {"model": MessageResponse, "description": "Forbidden"},
        404: {"model": MessageResponse, "description": "Not Found"},
        500: {"model": MessageResponse, "description": "Internal Server Error"}
    }
)


async def validate_token(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme. Use Bearer"
            )

        payload, is_valid = verify_and_decode_token(token, expected_type="access")
        if not is_valid or not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return payload
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use 'Bearer &lt;token&gt;'"
        )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    description=(
        "Register a new user and receive access tokens. "
        "The response will include instructions on how to use the token."
    ),
    responses={
        201: {
            "model": AuthResponse,
            "description": "User successfully registered with tokens",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "is_active": True,
                            "roles": []
                        },
                        "tokens": {
                            "access_token": "eyJhbGciOiJIUzI1NiIs...",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                            "token_type": "Bearer",
                            "expires_in": 1800,
                            "authorization_header": "Bearer eyJhbGciOiJIUzI1NiIs...",
                            "usage_instructions": "Add this header to your requests: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
                        },
                        "message": "Registration successful. Use the authorization_header from tokens in your requests."
                    }
                }
            }
        },
        400: {"model": MessageResponse, "description": "Invalid registration data"},
        500: {"model": MessageResponse, "description": "Server error"}
    }
)
async def register_user(
        user_data: UserRegisterRequest,
        session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    try:
        logger.debug(f"Attempting to register user with email: {user_data.email}")
        controller = AuthController(session)
        user, tokens = await controller.register_user(user_data)
        logger.info(f"Successfully registered user with email: {user_data.email}")

        return AuthResponse(
            user=user,
            tokens=TokenResponse(**tokens),
            message=(
                f"Registration successful. Add this header to your requests: "
                f"Authorization: Bearer {tokens['access_token']}"
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    description=(
        "Authenticate user and receive access token. "
        "The response will include detailed instructions on how to use the token."
    ),
    responses={
        200: {
            "model": AuthResponse,
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "is_active": True,
                            "roles": []
                        },
                        "tokens": {
                            "access_token": "eyJhbGciOiJIUzI1NiIs...",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                            "token_type": "Bearer",
                            "expires_in": 1800,
                            "authorization_header": "Bearer eyJhbGciOiJIUzI1NiIs...",
                            "usage_instructions": "Add this header to your requests: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
                        },
                        "message": "Successfully authenticated. Add this header to your requests: Authorization: Bearer {tokens['access_token']}"
                    }
                }
            }
        },
        401: {"model": MessageResponse, "description": "Invalid credentials"},
        500: {"model": MessageResponse, "description": "Server error"}
    }
)
async def login_user(
        user_data: UserLoginRequest,
        session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    try:
        logger.debug(f"Login attempt for user: {user_data.email}")
        controller = AuthController(session)
        user, tokens = await controller.login_user(user_data)
        logger.info(f"Successful login for user: {user_data.email}")

        return AuthResponse(
            user=user,
            tokens=TokenResponse(**tokens),
            message=(
                f"Successfully authenticated. Add this header to your requests: "
                f"Authorization: Bearer {tokens['access_token']}"
            )
        )
    except HTTPException as e:
        logger.warning(f"Login failed for user {user_data.email}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    description=(
        "Logout user and invalidate the refresh token. "
        "Requires a valid access token in the Authorization header."
    ),
    responses={
        200: {"model": MessageResponse, "description": "Successfully logged out"},
        401: {"model": MessageResponse, "description": "Not authenticated"},
        500: {"model": MessageResponse, "description": "Server error"}
    }
)
async def logout_user(
        logout_data: LogoutRequest,
        authorization: Optional[str] = Header(None),
        session: AsyncSession = Depends(get_session)
) -> MessageResponse:
    try:
        payload = await validate_token(authorization)
        user_id = payload.get('sub')

        logger.debug(f"Attempting to logout user ID: {user_id}")
        controller = AuthController(session)
        await controller.logout_user(logout_data.refresh_token, authorization)

        logger.info(f"Successfully logged out user ID: {user_id}")
        return MessageResponse(message="Successfully logged out. Your tokens have been invalidated.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed due to server error"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    description=(
        "Get current user information (requires authentication). "
        "Add the Authorization header with your access token: "
        "Authorization: Bearer &lt;your_access_token&gt;"
    ),
    responses={
        200: {"model": UserResponse, "description": "Current user data"},
        401: {
            "model": MessageResponse,
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid Authorization header format. Use 'Bearer &lt;token&gt;'",
                        "status_code": 401,
                        "error": "Authentication Error"
                    }
                }
            }
        },
        403: {"model": MessageResponse, "description": "Forbidden"},
        404: {"model": MessageResponse, "description": "User not found"},
        500: {"model": MessageResponse, "description": "Server error"}
    }
)
async def get_current_user(
        authorization: Optional[str] = Header(None),
        session: AsyncSession = Depends(get_session)
) -> UserResponse:
    try:
        payload = await validate_token(authorization)
        user_id = int(payload.get('sub'))

        logger.debug(f"Fetching data for user ID: {user_id}")
        user = await session.get(User, user_id, options=[selectinload(User.roles)])

        if not user:
            logger.error(f"User not found for ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            logger.warning(f"Attempt to access deactivated account: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        logger.info(f"Successfully retrieved data for user ID: {user_id}")
        return UserResponse.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user data"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    description="Refresh access token using refresh token",
    responses={
        200: {
            "model": TokenResponse,
            "description": "New access token",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIs...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                        "token_type": "Bearer",
                        "expires_in": 1800,
                        "authorization_header": "Bearer eyJhbGciOiJIUzI1NiIs...",
                        "usage_instructions": "Add this header to your requests: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
                    }
                }
            }
        },
        401: {"model": MessageResponse, "description": "Invalid refresh token"},
        500: {"model": MessageResponse, "description": "Server error"}
    }
)
async def refresh_token(
        refresh_data: TokenRefreshRequest,
        session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    try:
        logger.debug("Token refresh requested")
        controller = AuthController(session)
        tokens = await controller.refresh_tokens(refresh_data.refresh_token)
        logger.info("Access token successfully refreshed")
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please try logging in again."
        )


@router.post(
    "/bulk-update-roles",
    response_model=MessageResponse,
    description="Bulk update user roles",
    responses={
        200: {"model": MessageResponse, "description": "Roles updated successfully"},
        400: {"model": MessageResponse, "description": "Invalid request data"},
        401: {"model": MessageResponse, "description": "Not authenticated"},
        403: {"model": MessageResponse, "description": "Insufficient permissions"},
        500: {"model": MessageResponse, "description": "Server error"}
    }
)
async def bulk_update_user_roles(
        bulk_data: BulkRoleUpdateRequest,
        authorization: Optional[str] = Header(None),
        session: AsyncSession = Depends(get_session)
) -> MessageResponse:
    try:
        await validate_token(authorization)

        logger.debug(f"Bulk updating roles for {len(bulk_data.user_ids)} users")
        controller = AuthController(session)
        await controller.bulk_update_user_roles(bulk_data)

        return MessageResponse(message=f"Successfully updated roles for {len(bulk_data.user_ids)} users")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk role update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk role update failed"
        )


@router.post(
    "/verify-token",
    response_model=MessageResponse,
    description="Verify the validity of an access token",
    responses={
        200: {"model": MessageResponse, "description": "Token is valid"},
        401: {"model": MessageResponse, "description": "Invalid or expired token"},
    }
)
async def verify_token(
        authorization: Optional[str] = Header(None)
) -> MessageResponse:
    try:
        await validate_token(authorization)
        return MessageResponse(message="Token is valid")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
