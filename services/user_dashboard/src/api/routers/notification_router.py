from fastapi import APIRouter, Depends, status
from typing import List

from src.api.controllers import NotificationController
from src.api.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationUpdate,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    responses={
         401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
    dependencies=[Depends(AuthMiddleware())],
)


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Get a list of all notifications for current user",
)
async def get_all_notifications(controller: NotificationController = Depends()) -> NotificationListResponse:
    """
    Retrieves all notifications for the current user.
    """
    return await controller.get_notifications()


@router.put(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Update an existing notification",
)
async def update_notification(
    notification_id: int, notification_data: NotificationUpdate, controller: NotificationController = Depends()
) -> NotificationResponse:
    """
    Updates an existing notification with new data.
    """
    return await controller.update_notification(notification_id=notification_id, notification_data=notification_data)