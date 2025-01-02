from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from passlib.context import CryptContext

from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.db.repositories import UserRepository
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.core.utils.exceptions import ValidationException

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class UserManager:
    """
    Manages user-related business logic in the User Dashboard.
    """

    def __init__(self, user_repository: UserRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = user_repository
        self.session = session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @handle_exceptions
    async def create_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Creates a new user.
        """
        logging_client.info(f"Creating user with email: {email}")
        if not email or not password:
           logging_client.warning("Email and password cannot be empty")
           raise ValidationException("Email and password are required")
        hashed_password = self.pwd_context.hash(password)
        try:
            user = await self.repository.create(email=email, hashed_password=hashed_password)
            logging_client.info(f"User with email: {email} created successfully with ID: {user.id}")
            return user.__dict__
        except Exception as e:
             logging_client.error(f"Error creating user with email {email}: {e}")
             raise
    
    @handle_exceptions
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user by its ID.
        """
        logging_client.info(f"Getting user with ID: {user_id}")
        try:
            user = await self.repository.get(user_id=user_id)
            if not user:
                logging_client.warning(f"User with ID {user_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                 )
            logging_client.info(f"User with ID {user_id} retrieved successfully.")
            return user.__dict__
        except Exception as e:
            logging_client.error(f"Error getting user {user_id}: {e}")
            raise


    @handle_exceptions
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Retrieves all users.
        """
        logging_client.info("Getting all users")
        try:
            users = await self.repository.get_all()
            logging_client.info(f"Successfully retrieved {len(users)} users.")
            return [user.__dict__ for user in users]
        except Exception as e:
            logging_client.error(f"Error getting all users: {e}")
            raise

    @handle_exceptions
    async def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing user.
        """
        logging_client.info(f"Updating user with ID: {user_id}")
        try:
            user = await self.repository.update(user_id=user_id, email=email, is_active=is_active)
            if not user:
                logging_client.warning(f"User with ID {user_id} not found")
                raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logging_client.info(f"User with ID {user_id} updated successfully.")
            return user.__dict__
        except Exception as e:
            logging_client.error(f"Error updating user with ID {user_id}: {e}")
            raise


    @handle_exceptions
    async def delete_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Deletes a user by its ID.
        """
        logging_client.info(f"Deleting user with ID: {user_id}")
        try:
            user = await self.repository.delete(user_id=user_id)
            if not user:
                logging_client.warning(f"User with ID {user_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                 )
            logging_client.info(f"User with ID {user_id} deleted successfully.")
            return user.__dict__
        except Exception as e:
            logging_client.error(f"Error deleting user with ID {user_id}: {e}")
            raise
    
    @handle_exceptions
    async def block_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Blocks a user by its ID.
        """
        logging_client.info(f"Blocking user with ID: {user_id}")
        try:
            user = await self.repository.update(user_id=user_id, is_active=False)
            if not user:
               logging_client.warning(f"User with ID {user_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                 )
            logging_client.info(f"User with ID {user_id} blocked successfully.")
            return user.__dict__
        except Exception as e:
             logging_client.error(f"Error blocking user with ID: {user_id}: {e}")
             raise
    
    @handle_exceptions
    async def unblock_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Unblocks a user by their ID.
        """
        logging_client.info(f"Unblocking user with ID: {user_id}")
        try:
            user = await self.repository.update(user_id=user_id, is_active=True)
            if not user:
               logging_client.warning(f"User with ID {user_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            logging_client.info(f"User with ID {user_id} unblocked successfully.")
            return user.__dict__
        except Exception as e:
             logging_client.error(f"Error unblocking user with ID {user_id}: {e}")
             raise