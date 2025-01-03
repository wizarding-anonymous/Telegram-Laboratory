import pytest
from unittest.mock import AsyncMock
from src.api.controllers.analytics_controller import AnalyticsController
from src.core.utils.exceptions import AuthenticationException, AuthorizationException
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_get_overview_analytics_success(mock_auth_service: AsyncMock):
    """
    Test successful retrieval of overview analytics.
    """
    controller = AnalyticsController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.get_overview_analytics(token="test_token")

    assert isinstance(result, dict)
    assert "total_bots" in result
    assert "total_messages" in result
    assert "active_users" in result


@pytest.mark.asyncio
async def test_get_overview_analytics_unauthorized(mock_auth_service: AsyncMock):
    """
    Test retrieval of overview analytics when user is unauthorized.
    """
    controller = AnalyticsController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.get_overview_analytics(token="invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"


@pytest.mark.asyncio
async def test_get_bot_analytics_success(mock_auth_service: AsyncMock):
    """
    Test successful retrieval of analytics for a specific bot.
    """
    controller = AnalyticsController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.get_bot_analytics(token="test_token", bot_id=1)

    assert isinstance(result, dict)
    assert "total_messages" in result
    assert "active_users" in result
    assert "error_count" in result

@pytest.mark.asyncio
async def test_get_bot_analytics_unauthorized(mock_auth_service: AsyncMock):
    """
     Test retrieval of bot analytics when user is unauthorized
    """
    controller = AnalyticsController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
         await controller.get_bot_analytics(token="invalid_token", bot_id=1)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_get_bot_analytics_unauthorized_admin(mock_auth_service_admin: AsyncMock):
    """
    Test retrieval of bot analytics when user is an admin but not authorized for that endpoint.
    """
    controller = AnalyticsController(auth_service=mock_auth_service_admin)
    mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    with pytest.raises(HTTPException) as exc_info:
        await controller.get_bot_analytics(token="test_token", bot_id=1)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Authorization failed"