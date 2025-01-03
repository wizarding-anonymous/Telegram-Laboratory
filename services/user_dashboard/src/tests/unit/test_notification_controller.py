import pytest
from unittest.mock import AsyncMock
from src.api.controllers.notification_controller import NotificationController
from src.core.utils.exceptions import AuthenticationException, AuthorizationException
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_user_notifications_success(mock_auth_service: AsyncMock):
    """
    Test successful retrieval of user notifications.
    """
    controller = NotificationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.get_user_notifications(token="test_token")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_user_notifications_unauthorized(mock_auth_service: AsyncMock):
    """
    Test retrieval of user notifications when user is unauthorized.
    """
    controller = NotificationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.get_user_notifications(token="invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"


@pytest.mark.asyncio
async def test_update_notification_success(mock_auth_service: AsyncMock):
    """
    Test successful update of a notification.
    """
    controller = NotificationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.update_notification(token="test_token", notification_id=1, notification_data={"status": "read"})
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.asyncio
async def test_update_notification_unauthorized(mock_auth_service: AsyncMock):
    """
    Test update of a notification when user is unauthorized.
    """
    controller = NotificationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.update_notification(token="invalid_token", notification_id=1, notification_data={"status": "read"})
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_update_notification_unauthorized_admin(mock_auth_service_admin: AsyncMock):
     """
     Test update of a notification when user is an admin but unauthorized for that endpoint.
     """
     controller = NotificationController(auth_service=mock_auth_service_admin)
     mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     with pytest.raises(HTTPException) as exc_info:
         await controller.update_notification(token="test_token", notification_id=1, notification_data={"status": "read"})
     assert exc_info.value.status_code == 403
     assert exc_info.value.detail == "Authorization failed"