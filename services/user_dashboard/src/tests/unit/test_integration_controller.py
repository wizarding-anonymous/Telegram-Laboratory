import pytest
from unittest.mock import AsyncMock
from src.api.controllers.integration_controller import IntegrationController
from src.core.utils.exceptions import AuthenticationException, AuthorizationException
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_get_user_integrations_success(mock_auth_service: AsyncMock):
    """
    Test successful retrieval of user integrations.
    """
    controller = IntegrationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.get_user_integrations(token="test_token")

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_user_integrations_unauthorized(mock_auth_service: AsyncMock):
    """
    Test retrieval of user integrations when user is unauthorized.
    """
    controller = IntegrationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
         await controller.get_user_integrations(token="invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"


@pytest.mark.asyncio
async def test_add_integration_success(mock_auth_service: AsyncMock):
    """
    Test successful creation of a integration.
    """
    controller = IntegrationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.add_integration(token="test_token", integration_data={"service": "test_service", "api_key": "test_key"})
    assert isinstance(result, dict)
    assert "id" in result
    assert "service" in result


@pytest.mark.asyncio
async def test_add_integration_unauthorized(mock_auth_service: AsyncMock):
    """
    Test add integration when user is unauthorized.
    """
    controller = IntegrationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.add_integration(token="invalid_token", integration_data={"service": "test_service", "api_key": "test_key"})
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_delete_integration_success(mock_auth_service: AsyncMock):
    """
    Test successful deletion of an integration.
    """
    controller = IntegrationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.delete_integration(token="test_token", integration_id=1)
    assert isinstance(result, dict)
    assert "message" in result

@pytest.mark.asyncio
async def test_delete_integration_unauthorized(mock_auth_service: AsyncMock):
    """
    Test deletion of integration when user is unauthorized.
    """
    controller = IntegrationController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.delete_integration(token="invalid_token", integration_id=1)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_delete_integration_unauthorized_admin(mock_auth_service_admin: AsyncMock):
     """
     Test deletion of integration when user is admin but unauthorized for that endpoint.
     """
     controller = IntegrationController(auth_service=mock_auth_service_admin)
     mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     with pytest.raises(HTTPException) as exc_info:
         await controller.delete_integration(token="test_token", integration_id=1)

     assert exc_info.value.status_code == 403
     assert exc_info.value.detail == "Authorization failed"