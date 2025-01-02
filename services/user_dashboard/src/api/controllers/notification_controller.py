from typing import List
from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.notification_manager import NotificationManager
from src.api.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationUpdate,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.integrations.logging_client import LoggingClient
from src.api.middleware.auth import auth_required
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class NotificationController:
    """
    Controller for handling notification-related operations in the User Dashboard.
    """

    def __init__(self, notification_manager: NotificationManager = Depends(), session: AsyncSession = Depends(get_session)):
        self.notification_manager = notification_manager
        self.session = session


    @handle_exceptions
    async def get_notifications(self, user: dict = Depends(auth_required)) -> NotificationListResponse:
        """
        Retrieves a list of notifications for the current user.
        """
        logging_client.info(f"Getting notifications for user {user['id']}")
        try:
            notifications = await self.notification_manager.get_notifications(user_id=user['id'])
            logging_client.info(f"Successfully retrieved {len(notifications)} notifications for user: {user['id']}")
            return NotificationListResponse(
                items=[NotificationResponse(**notification.__dict__) for notification in notifications]
            )
        except Exception as e:
           logging_client.error(f"Failed to get notifications for user {user['id']}: {e}")
           raise
        

    @handle_exceptions
    async def update_notification(self, notification_id: int, notification_data: NotificationUpdate, user: dict = Depends(auth_required)) -> NotificationResponse:
        """
        Updates the status of a notification.
        """
        logging_client.info(f"Updating notification with id {notification_id} for user {user['id']}")
        try:
             notification = await self.notification_manager.update_notification(
                 notification_id=notification_id, user_id=user['id'], status=notification_data.status
             )
             if not notification:
                 logging_client.warning(f"Notification with ID {notification_id} not found for user {user['id']}")
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found",
                )
             logging_client.info(f"Notification with id {notification_id} updated successfully for user: {user['id']}")
             return NotificationResponse(**notification.__dict__)
        except Exception as e:
            logging_client.error(f"Failed to update notification with id {notification_id} for user {user['id']}: {e}")
            raise