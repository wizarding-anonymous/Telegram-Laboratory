import pytest
from unittest.mock import AsyncMock
from src.api.controllers.user_controller import UserController
from src.core.utils.exceptions import AuthenticationException, AuthorizationException
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_user_profile_success(mock_auth_service: AsyncMock):
    """
    Test successful retrieval of user profile.
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}
    result = await controller.get_user_profile(token="test_token")
    assert isinstance(result, dict)
    assert "id" in result
    assert "email" in result


@pytest.mark.asyncio
async def test_get_user_profile_unauthorized(mock_auth_service: AsyncMock):
    """
    Test retrieval of user profile when user is unauthorized.
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.get_user_profile(token="invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_update_user_profile_success(mock_auth_service: AsyncMock):
    """
    Test successful update of user profile.
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.update_user_profile(token="test_token", user_data={"name": "new_name", "email": "test@test.com"})
    assert isinstance(result, dict)
    assert "message" in result


@pytest.mark.asyncio
async def test_update_user_profile_unauthorized(mock_auth_service: AsyncMock):
    """
    Test update of a user profile when user is unauthorized.
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.update_user_profile(token="invalid_token", user_data={"name": "new_name", "email": "test@test.com"})
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_update_user_profile_unauthorized_admin(mock_auth_service_admin: AsyncMock):
     """
     Test update of user profile when user is an admin but unauthorized for that endpoint.
     """
     controller = UserController(auth_service=mock_auth_service_admin)
     mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     with pytest.raises(HTTPException) as exc_info:
         await controller.update_user_profile(token="test_token", user_data={"name": "new_name", "email": "test@test.com"})
     assert exc_info.value.status_code == 403
     assert exc_info.value.detail == "Authorization failed"


@pytest.mark.asyncio
async def test_reset_password_success(mock_auth_service: AsyncMock):
    """
    Test successful reset password request.
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.reset_password(token="test_token", user_data={"email": "test@test.com"})
    assert isinstance(result, dict)
    assert "message" in result

@pytest.mark.asyncio
async def test_reset_password_unauthorized(mock_auth_service: AsyncMock):
    """
     Test reset password when user is unauthorized
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.reset_password(token="invalid_token", user_data={"email": "test@test.com"})
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_reset_password_unauthorized_admin(mock_auth_service_admin: AsyncMock):
     """
     Test reset password when user is an admin but unauthorized for that endpoint.
     """
     controller = UserController(auth_service=mock_auth_service_admin)
     mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     with pytest.raises(HTTPException) as exc_info:
        await controller.reset_password(token="test_token", user_data={"email": "test@test.com"})
     assert exc_info.value.status_code == 403
     assert exc_info.value.detail == "Authorization failed"

@pytest.mark.asyncio
async def test_change_password_success(mock_auth_service: AsyncMock):
    """
    Test successful change password.
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.change_password(token="test_token", user_data={"old_password": "old_password", "new_password": "new_password"})
    assert isinstance(result, dict)
    assert "message" in result

@pytest.mark.asyncio
async def test_change_password_unauthorized(mock_auth_service: AsyncMock):
    """
    Test change password when user is unauthorized.
    """
    controller = UserController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
         await controller.change_password(token="invalid_token", user_data={"old_password": "old_password", "new_password": "new_password"})
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_change_password_unauthorized_admin(mock_auth_service_admin: AsyncMock):
     """
     Test change password when user is admin but unauthorized for that endpoint.
     """
     controller = UserController(auth_service=mock_auth_service_admin)
     mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     with pytest.raises(HTTPException) as exc_info:
         await controller.change_password(token="test_token", user_data={"old_password": "old_password", "new_password": "new_password"})
     assert exc_info.value.status_code == 403
     assert exc_info.value.detail == "Authorization failed"