import pytest
from unittest.mock import AsyncMock
from src.api.controllers.health_controller import HealthController
from src.core.utils.exceptions import AuthenticationException
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_health_check_success(mock_auth_service: AsyncMock):
    """
    Test successful health check.
    """
    controller = HealthController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}
    response = await controller.health_check(token="test_token")
    assert response == {"status": "ok", "details": "Service is healthy"}


@pytest.mark.asyncio
async def test_health_check_unauthorized(mock_auth_service: AsyncMock):
    """
    Test health check when user is unauthorized.
    """
    controller = HealthController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
         await controller.health_check(token="invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"