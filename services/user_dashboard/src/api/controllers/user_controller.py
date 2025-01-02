from typing import List, Optional
from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.user_manager import UserManager
from src.api.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.integrations.logging_client import LoggingClient
from src.api.middleware.auth import admin_required
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class UserController:
    """
    Controller for handling user-related operations in the User Dashboard microservice.
    """

    def __init__(self, user_manager: UserManager = Depends(), session: AsyncSession = Depends(get_session)):
        self.user_manager = user_manager
        self.session = session

    @handle_exceptions
    async def create_user(self, user_data: UserCreate, user: dict = Depends(admin_required)) -> UserResponse:
        """
        Creates a new user (only admin users can do this).
        """
        logging_client.info(f"Creating new user with email: {user_data.email} by user {user['id']}")
        try:
            user = await self.user_manager.create_user(
                email=user_data.email, password=user_data.password
            )
            logging_client.info(f"User with email {user_data.email} created successfully by user {user['id']}. User ID: {user.id}")
            return UserResponse(**user.__dict__)
        except Exception as e:
             logging_client.error(f"Failed to create user with email {user_data.email} by user {user['id']}: {e}")
             raise

    @handle_exceptions
    async def get_user(self, user_id: int, user: dict = Depends(admin_required)) -> UserResponse:
        """
        Retrieves a user by their ID (only admin users can do this).
        """
        logging_client.info(f"Getting user with ID: {user_id} by user {user['id']}")
        try:
            user = await self.user_manager.get_user(user_id=user_id)
            if not user:
                logging_client.warning(f"User with ID {user_id} not found by user {user['id']}")
                raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logging_client.info(f"User with id {user_id} retrieved successfully by user {user['id']}")
            return UserResponse(**user.__dict__)
        except Exception as e:
            logging_client.error(f"Failed to get user {user_id} by user {user['id']}: {e}")
            raise

    @handle_exceptions
    async def get_all_users(self, user: dict = Depends(admin_required)) -> UserListResponse:
        """
        Retrieves all users (only admin users can do this).
        """
        logging_client.info(f"Getting all users by user {user['id']}")
        try:
            users = await self.user_manager.get_all_users()
            logging_client.info(f"Successfully retrieved {len(users)} users for user {user['id']}")
            return UserListResponse(items=[UserResponse(**user.__dict__) for user in users])
        except Exception as e:
             logging_client.error(f"Failed to get all users by user {user['id']}: {e}")
             raise

    @handle_exceptions
    async def update_user(self, user_id: int, user_data: UserUpdate, user: dict = Depends(admin_required)) -> UserResponse:
        """
        Updates an existing user (only admin users can do this).
        """
        logging_client.info(f"Updating user with ID: {user_id} for user {user['id']}")
        try:
            user = await self.user_manager.update_user(
                user_id=user_id,
                email=user_data.email,
                is_active=user_data.is_active,
            )
            if not user:
               logging_client.warning(f"User with ID {user_id} not found for update for user {user['id']}")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                 )
            logging_client.info(f"User with ID {user_id} updated successfully for user {user['id']}")
            return UserResponse(**user.__dict__)
        except Exception as e:
             logging_client.error(f"Failed to update user {user_id} for user {user['id']}: {e}")
             raise


    @handle_exceptions
    async def delete_user(self, user_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Deletes a user by their ID (only admin users can do this).
        """
        logging_client.info(f"Deleting user with ID: {user_id} for user {user['id']}")
        try:
            user = await self.user_manager.delete_user(user_id=user_id)
            if not user:
               logging_client.warning(f"User with ID {user_id} not found for deletion for user {user['id']}")
               raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
               )
            logging_client.info(f"User with id {user_id} deleted successfully for user {user['id']}.")
            return SuccessResponse(message="User deleted successfully")
        except Exception as e:
            logging_client.error(f"Failed to delete user {user_id} for user {user['id']}: {e}")
            raise