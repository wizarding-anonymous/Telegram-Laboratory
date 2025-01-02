from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import UserData
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class UserDataRepository:
    """
    Repository for performing CRUD operations on the UserData model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, user_id: int, bot_id: int, analytics: dict, metadata: dict) -> UserData:
        """
        Creates a new user data entry in the database.
        """
        logger.info(f"Creating user data for user: {user_id} and bot: {bot_id}")
        try:
            user_data = UserData(user_id=user_id, bot_id=bot_id, analytics=analytics, metadata=metadata)
            self.session.add(user_data)
            await self.session.commit()
            await self.session.refresh(user_data)
            logger.info(f"User data created successfully with id: {user_data.id}")
            return user_data
        except Exception as e:
            logger.error(f"Error creating user data for user {user_id} and bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to create user data for user {user_id} and bot {bot_id}: {e}") from e


    @handle_exceptions
    async def get(self, user_data_id: int) -> Optional[UserData]:
        """
        Retrieves user data by its ID.
        """
        logger.info(f"Getting user data with ID: {user_data_id}")
        try:
            query = select(UserData).where(UserData.id == user_data_id)
            result = await self.session.execute(query)
            user_data = result.scalar_one_or_none()
            if user_data:
                logger.debug(f"User data with ID {user_data_id} found.")
            else:
                logger.warning(f"User data with ID {user_data_id} not found.")
            return user_data
        except Exception as e:
            logger.error(f"Error getting user data with ID {user_data_id}: {e}")
            raise DatabaseException(f"Failed to get user data with id {user_data_id}: {e}") from e

    @handle_exceptions
    async def get_by_bot_id_and_user_id(self, bot_id: int, user_id: int) -> Optional[UserData]:
        """
        Retrieves user data by bot ID and user ID.
        """
        logger.info(f"Getting user data for bot ID: {bot_id}, user ID: {user_id}")
        try:
            query = select(UserData).where(UserData.bot_id == bot_id, UserData.user_id == user_id)
            result = await self.session.execute(query)
            user_data = result.scalar_one_or_none()
            if user_data:
               logger.debug(f"User data for bot {bot_id} and user {user_id} found")
            else:
               logger.warning(f"User data for bot {bot_id} and user {user_id} not found")
            return user_data
        except Exception as e:
            logger.error(f"Error getting user data for bot {bot_id} and user {user_id}: {e}")
            raise DatabaseException(f"Failed to get user data for bot {bot_id} and user {user_id}: {e}") from e


    @handle_exceptions
    async def get_all_by_user_id(self, user_id: int) -> List[UserData]:
        """
        Retrieves all user data entries for a specific user ID.
        """
        logger.info(f"Getting all user data for user ID: {user_id}")
        try:
           query = select(UserData).where(UserData.user_id == user_id)
           result = await self.session.execute(query)
           user_data_list = list(result.scalars().all())
           logger.debug(f"Found {len(user_data_list)} user data entries for user {user_id}")
           return user_data_list
        except Exception as e:
           logger.error(f"Error getting all user data for user {user_id}: {e}")
           raise DatabaseException(f"Failed to get all user data for user {user_id}: {e}") from e


    @handle_exceptions
    async def update(self, user_data_id: int, **user_data_values) -> Optional[UserData]:
        """
        Updates existing user data by its ID.
        """
        logger.info(f"Updating user data with ID: {user_data_id}, data: {user_data_values}")
        try:
            query = select(UserData).where(UserData.id == user_data_id)
            result = await self.session.execute(query)
            user_data = result.scalar_one_or_none()
            if user_data:
                for key, value in user_data_values.items():
                    setattr(user_data, key, value)
                await self.session.commit()
                await self.session.refresh(user_data)
                logger.info(f"User data with ID {user_data_id} updated successfully")
            else:
                logger.warning(f"User data with ID {user_data_id} not found for update.")
            return user_data
        except Exception as e:
            logger.error(f"Error updating user data {user_data_id}: {e}")
            raise DatabaseException(f"Failed to update user data with id {user_data_id}: {e}") from e

    @handle_exceptions
    async def delete(self, user_data_id: int) -> Optional[UserData]:
        """
        Deletes a user data entry by its ID.
        """
        logger.info(f"Deleting user data with ID: {user_data_id}")
        try:
            query = delete(UserData).where(UserData.id == user_data_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"User data with ID {user_data_id} deleted successfully.")
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error deleting user data with ID {user_data_id}: {e}")
            raise DatabaseException(f"Failed to delete user data with id {user_data_id}: {e}") from e