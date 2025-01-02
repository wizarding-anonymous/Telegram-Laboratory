from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.db.repositories import NotificationRepository
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class NotificationManager:
    """
    Manages notification-related business logic for the User Dashboard.
    """

    def __init__(self, notification_repository: NotificationRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = notification_repository
        self.session = session

    @handle_exceptions
    async def get_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves a list of notifications for a specific user.
        """
        logging_client.info(f"Getting notifications for user: {user_id}")
        try:
            notifications = await self.repository.get_all_by_user_id(user_id=user_id)
            logging_client.info(f"Successfully retrieved {len(notifications)} for user: {user_id}")
            return [notification.__dict__ for notification in notifications]
        except Exception as e:
            logging_client.error(f"Error getting notifications for user {user_id}: {e}")
            raise

    @handle_exceptions
    async def update_notification(self, notification_id: int, user_id: int, status: str) -> Optional[Dict[str, Any]]:
        """
        Updates an existing notification.
        """
        logging_client.info(f"Updating notification with ID: {notification_id} for user {user_id}")
        try:
            notification = await self.repository.update(notification_id=notification_id, user_id=user_id, status=status)
            if not notification:
                 logging_client.warning(f"Notification with id: {notification_id} not found for user: {user_id}")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
                 )
            logging_client.info(f"Notification with ID {notification_id} updated successfully for user: {user_id}")
            return notification.__dict__
        except Exception as e:
            logging_client.error(f"Error updating notification {notification_id} for user {user_id}: {e}")
            raise