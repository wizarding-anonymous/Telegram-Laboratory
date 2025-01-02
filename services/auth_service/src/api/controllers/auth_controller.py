from typing import Optional

from fastapi import Depends, HTTPException, status
from loguru import logger

from src.core.auth_manager import AuthManager
from src.api.schemas import (
    AuthLogin,
    AuthResponse,
    AuthRegister,
    AuthRefresh,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AuthController:
    """
    Controller for handling authentication-related operations.
    """

    def __init__(self, auth_manager: AuthManager = Depends()):
        self.auth_manager = auth_manager

    @handle_exceptions
    async def register_user(self, user_data: AuthRegister) -> SuccessResponse:
        """
        Registers a new user.
        """
        logging_client.info(f"Attempting to register user: {user_data.email}")
        try:
           await self.auth_manager.register_user(
               email=user_data.email, password=user_data.password
           )
           logging_client.info(f"User registered successfully: {user_data.email}")
           return SuccessResponse(message="User registered successfully")
        except Exception as e:
            logging_client.error(f"Failed to register user: {e}")
            raise

    @handle_exceptions
    async def login_user(self, login_data: AuthLogin) -> AuthResponse:
        """
        Authenticates a user and returns access and refresh tokens.
        """
        logging_client.info(f"Attempting login for user: {login_data.email}")
        try:
           tokens = await self.auth_manager.login_user(
               email=login_data.email, password=login_data.password
           )
           logging_client.info(f"User logged in successfully: {login_data.email}")
           return AuthResponse(**tokens)
        except Exception as e:
            logging_client.error(f"Login failed for user: {login_data.email}. Error: {e}")
            raise

    @handle_exceptions
    async def logout_user(self, token_data: AuthRefresh) -> SuccessResponse:
        """
        Logs out a user by invalidating the refresh token.
        """
        logging_client.info("Attempting user logout")
        try:
            await self.auth_manager.logout_user(refresh_token=token_data.refresh_token)
            logging_client.info("User logged out successfully.")
            return SuccessResponse(message="User logged out successfully")
        except Exception as e:
           logging_client.error(f"Logout failed. Error: {e}")
           raise

    @handle_exceptions
    async def get_current_user(self, token: str) -> Optional[dict]:
        """
        Retrieves the current user based on the access token.
        """
        logging_client.info("Getting current user info from token")
        try:
            user = await self.auth_manager.get_user_by_token(access_token=token)
            if user:
                logging_client.info(f"Current user info retrieved successfully")
                return user
            else:
                logging_client.warning("Invalid or expired token provided.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
                )

        except Exception as e:
           logging_client.error(f"Error getting current user: {e}")
           raise
    
    @handle_exceptions
    async def refresh_token(self, token_data: AuthRefresh) -> AuthResponse:
         """
         Refreshes the access token using the refresh token.
         """
         logging_client.info("Attempting to refresh access token.")
         try:
             tokens = await self.auth_manager.refresh_token(refresh_token=token_data.refresh_token)
             logging_client.info("Access token refreshed successfully.")
             return AuthResponse(**tokens)
         except Exception as e:
             logging_client.error(f"Token refresh failed. Error: {e}")
             raise