from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import User
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class UserRepository:
    """
    Repository for performing CRUD operations on the User model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, email: str, hashed_password: str) -> User:
        """
        Creates a new user in the database.
        """
        logger.info(f"Creating user with email: {email}")
        try:
            user = User(email=email, hashed_password=hashed_password)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"User with email: {email} created successfully with id: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Error creating user with email {email}: {e}")
            raise DatabaseException(f"Failed to create user: {e}") from e


    @handle_exceptions
    async def get(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by their ID.
        """
        logger.info(f"Getting user with ID: {user_id}")
        try:
           query = select(User).where(User.id == user_id)
           result = await self.session.execute(query)
           user = result.scalar_one_or_none()
           if user:
               logger.debug(f"User with ID {user_id} found")
           else:
              logger.warning(f"User with ID {user_id} not found")
           return user
        except Exception as e:
           logger.error(f"Error getting user with ID {user_id}: {e}")
           raise DatabaseException(f"Failed to get user with id {user_id}: {e}") from e

    @handle_exceptions
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user by their email address.
        """
        logger.info(f"Getting user by email: {email}")
        try:
            query = select(User).where(User.email == email)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
            if user:
               logger.debug(f"User with email {email} found.")
            else:
               logger.warning(f"User with email {email} not found.")
            return user
        except Exception as e:
            logger.error(f"Error getting user with email {email}: {e}")
            raise DatabaseException(f"Failed to get user with email {email}: {e}") from e


    @handle_exceptions
    async def get_all(self) -> List[User]:
        """
        Retrieves all users.
        """
        logger.info("Getting all users")
        try:
            query = select(User)
            result = await self.session.execute(query)
            users = list(result.scalars().all())
            logger.debug(f"Found {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise DatabaseException(f"Failed to get all users: {e}") from e

    @handle_exceptions
    async def update(self, user_id: int, email: Optional[str] = None, is_active: Optional[bool] = None) -> Optional[User]:
        """
        Updates an existing user by their ID.
        """
        logger.info(f"Updating user with ID: {user_id}")
        try:
           query = select(User).where(User.id == user_id)
           result = await self.session.execute(query)
           user = result.scalar_one_or_none()
           if user:
                if email is not None:
                    user.email = email
                if is_active is not None:
                     user.is_active = is_active
                await self.session.commit()
                await self.session.refresh(user)
                logger.info(f"User with ID {user_id} updated successfully")
           else:
              logger.warning(f"User with ID {user_id} not found for update.")
           return user
        except Exception as e:
            logger.error(f"Error updating user with ID {user_id}: {e}")
            raise DatabaseException(f"Failed to update user with id {user_id}: {e}") from e

    @handle_exceptions
    async def delete(self, user_id: int) -> Optional[User]:
         """
        Deletes a user by its ID.
         """
         logger.info(f"Deleting user with ID: {user_id}")
         try:
             query = delete(User).where(User.id == user_id)
             result = await self.session.execute(query)
             await self.session.commit()
             logger.info(f"User with id {user_id} deleted successfully")
             return result.scalar_one_or_none()
         except Exception as e:
             logger.error(f"Error deleting user with ID: {user_id}: {e}")
             raise DatabaseException(f"Failed to delete user with id {user_id}: {e}") from e