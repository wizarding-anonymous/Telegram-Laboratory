from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Notification
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class NotificationRepository:
    """
    Repository for performing CRUD operations on the Notification model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, user_id: int, type: str, message: str, timestamp: datetime, status:str) -> Notification:
        """
        Creates a new notification in the database.
        """
        logger.info(f"Creating notification with type: {type} for user: {user_id}")
        try:
            notification = Notification(user_id=user_id, type=type, message=message, timestamp=timestamp, status=status)
            self.session.add(notification)
            await self.session.commit()
            await self.session.refresh(notification)
            logger.info(f"Notification created successfully with id: {notification.id}")
            return notification
        except Exception as e:
           logger.error(f"Error creating notification for user {user_id}: {e}")
           raise DatabaseException(f"Failed to create notification for user {user_id}: {e}") from e


    @handle_exceptions
    async def get(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """
        Retrieves a notification by its ID.
        """
        logger.info(f"Getting notification with ID: {notification_id} for user: {user_id}")
        try:
            query = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
            result = await self.session.execute(query)
            notification = result.scalar_one_or_none()
            if notification:
                logger.debug(f"Notification with ID {notification_id} found")
            else:
                logger.warning(f"Notification with ID {notification_id} not found")
            return notification
        except Exception as e:
            logger.error(f"Error getting notification {notification_id}: {e}")
            raise DatabaseException(f"Failed to get notification with id {notification_id}: {e}") from e


    @handle_exceptions
    async def get_all_by_user_id(self, user_id: int) -> List[Notification]:
        """
        Retrieves all notifications for a specific user ID.
        """
        logger.info(f"Getting all notifications for user ID: {user_id}")
        try:
            query = select(Notification).where(Notification.user_id == user_id)
            result = await self.session.execute(query)
            notifications = list(result.scalars().all())
            logger.debug(f"Found {len(notifications)} notifications for user {user_id}")
            return notifications
        except Exception as e:
            logger.error(f"Error getting all notifications for user {user_id}: {e}")
            raise DatabaseException(f"Failed to get all notifications for user {user_id}: {e}") from e
        
    @handle_exceptions
    async def update(self, notification_id: int, user_id: int, status: str) -> Optional[Notification]:
        """
        Updates an existing notification by its ID.
        """
        logger.info(f"Updating notification with ID: {notification_id}, for user {user_id}, status: {status}")
        try:
           query = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
           result = await self.session.execute(query)
           notification = result.scalar_one_or_none()
           if notification:
                notification.status = status
                await self.session.commit()
                await self.session.refresh(notification)
                logger.info(f"Notification with ID {notification_id} updated successfully.")
           else:
               logger.warning(f"Notification with ID {notification_id} not found for update.")
           return notification
        except Exception as e:
            logger.error(f"Error updating notification with ID {notification_id}: {e}")
            raise DatabaseException(f"Failed to update notification with id {notification_id}: {e}") from e
    

    @handle_exceptions
    async def delete(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """
        Deletes a notification by its ID.
        """
        logger.info(f"Deleting notification with ID: {notification_id} for user: {user_id}")
        try:
            query = delete(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Notification with ID {notification_id} deleted successfully.")
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error deleting notification with ID {notification_id}: {e}")
            raise DatabaseException(f"Failed to delete notification with id {notification_id}: {e}") from e