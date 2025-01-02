from typing import List, Optional

from fastapi import Depends, HTTPException, status
from loguru import logger

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
from src.integrations.logging_client import LoggingClient
from src.api.middleware.auth import admin_required
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class UserController:
    """
    Controller for handling user-related operations.
    """

    def __init__(self, user_manager: UserManager = Depends()):
        self.user_manager = user_manager

    @handle_exceptions
    async def create_user(self, user_data: UserCreate, user: dict = Depends(admin_required)) -> UserResponse:
        """
        Creates a new user.
        """
        logging_client.info(f"Creating new user with email: {user_data.email}")
        try:
            user = await self.user_manager.create_user(
                email=user_data.email, password=user_data.password
            )
            logging_client.info(f"User created successfully. User id: {user.id}")
            return UserResponse(**user.__dict__)
        except Exception as e:
            logging_client.error(f"Failed to create user with email {user_data.email}: {e}")
            raise

    @handle_exceptions
    async def get_user(self, user_id: int, user: dict = Depends(admin_required)) -> UserResponse:
        """
        Retrieves a user by its ID.
        """
        logging_client.info(f"Getting user with ID: {user_id}")
        try:
            user = await self.user_manager.get_user(user_id=user_id)
            if not user:
               logging_client.warning(f"User with ID {user_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
               )
            logging_client.info(f"User retrieved successfully. User id: {user.id}")
            return UserResponse(**user.__dict__)
        except Exception as e:
             logging_client.error(f"Failed to get user with ID {user_id}: {e}")
             raise

    @handle_exceptions
    async def get_all_users(self, user: dict = Depends(admin_required)) -> UserListResponse:
        """
        Retrieves a list of all users.
        """
        logging_client.info("Getting all users")
        try:
            users = await self.user_manager.get_all_users()
            logging_client.info(f"Successfully retrieved {len(users)} users")
            return UserListResponse(items=[UserResponse(**user.__dict__) for user in users])
        except Exception as e:
             logging_client.error(f"Failed to get all users: {e}")
             raise

    @handle_exceptions
    async def update_user(self, user_id: int, user_data: UserUpdate, user: dict = Depends(admin_required)) -> UserResponse:
        """
        Updates an existing user.
        """
        logging_client.info(f"Updating user with ID: {user_id}")
        try:
            user = await self.user_manager.update_user(
                user_id=user_id,
                email=user_data.email,
                is_active=user_data.is_active,
            )
            if not user:
                logging_client.warning(f"User with id {user_id} not found")
                raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logging_client.info(f"User with ID {user_id} updated successfully")
            return UserResponse(**user.__dict__)
        except Exception as e:
            logging_client.error(f"Failed to update user with ID {user_id}: {e}")
            raise


    @handle_exceptions
    async def delete_user(self, user_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Deletes a user by its ID.
        """
        logging_client.info(f"Deleting user with ID: {user_id}")
        try:
            user = await self.user_manager.delete_user(user_id=user_id)
            if not user:
               logging_client.warning(f"User with id {user_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logging_client.info(f"User with id {user_id} deleted successfully.")
            return SuccessResponse(message="User deleted successfully")
        except Exception as e:
            logging_client.error(f"Failed to delete user with ID {user_id}: {e}")
            raise
    
    @handle_exceptions
    async def block_user(self, user_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Blocks user
        """
        logging_client.info(f"Blocking user with ID: {user_id}")
        try:
            user = await self.user_manager.block_user(user_id=user_id)
            if not user:
               logging_client.warning(f"User with id {user_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logging_client.info(f"User with id {user_id} blocked successfully.")
            return SuccessResponse(message="User blocked successfully")
        except Exception as e:
            logging_client.error(f"Failed to block user with ID {user_id}: {e}")
            raise
    
    @handle_exceptions
    async def unblock_user(self, user_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Unblocks user
        """
        logging_client.info(f"Unblocking user with ID: {user_id}")
        try:
            user = await self.user_manager.unblock_user(user_id=user_id)
            if not user:
               logging_client.warning(f"User with id {user_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logging_client.info(f"User with id {user_id} unblocked successfully.")
            return SuccessResponse(message="User unblocked successfully")
        except Exception as e:
            logging_client.error(f"Failed to unblock user with ID {user_id}: {e}")
            raise