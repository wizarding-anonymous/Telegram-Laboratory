import pytest
from unittest.mock import AsyncMock
from src.api.controllers.bot_controller import BotController
from src.core.utils.exceptions import AuthenticationException, AuthorizationException
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_user_bots_success(mock_auth_service: AsyncMock):
    """
    Test successful retrieval of user bots.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}
    result = await controller.get_user_bots(token="test_token")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_user_bots_unauthorized(mock_auth_service: AsyncMock):
    """
    Test retrieval of user bots when user is unauthorized.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.get_user_bots(token="invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"


@pytest.mark.asyncio
async def test_create_bot_success(mock_auth_service: AsyncMock):
    """
    Test successful creation of a bot.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.create_bot(token="test_token", bot_data={"name": "test_bot"})
    assert isinstance(result, dict)
    assert "id" in result
    assert "name" in result

@pytest.mark.asyncio
async def test_create_bot_unauthorized(mock_auth_service: AsyncMock):
    """
    Test creation of a bot when user is unauthorized.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
         await controller.create_bot(token="invalid_token", bot_data={"name": "test_bot"})
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"


@pytest.mark.asyncio
async def test_update_bot_success(mock_auth_service: AsyncMock):
    """
    Test successful update of a bot.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    result = await controller.update_bot(token="test_token", bot_id=1, bot_data={"name": "updated_bot"})
    assert isinstance(result, dict)
    assert "id" in result
    assert "name" in result
    assert "updated_at" in result


@pytest.mark.asyncio
async def test_update_bot_unauthorized(mock_auth_service: AsyncMock):
    """
    Test update of a bot when user is unauthorized.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException
    with pytest.raises(HTTPException) as exc_info:
         await controller.update_bot(token="invalid_token", bot_id=1, bot_data={"name": "updated_bot"})

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_update_bot_unauthorized_admin(mock_auth_service_admin: AsyncMock):
     """
     Test update of a bot when user is an admin but unauthorized for that endpoint.
     """
     controller = BotController(auth_service=mock_auth_service_admin)
     mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     with pytest.raises(HTTPException) as exc_info:
         await controller.update_bot(token="test_token", bot_id=1, bot_data={"name": "updated_bot"})

     assert exc_info.value.status_code == 403
     assert exc_info.value.detail == "Authorization failed"

@pytest.mark.asyncio
async def test_delete_bot_success(mock_auth_service: AsyncMock):
    """
    Test successful deletion of a bot.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}
    result = await controller.delete_bot(token="test_token", bot_id=1)

    assert result is None

@pytest.mark.asyncio
async def test_delete_bot_unauthorized(mock_auth_service: AsyncMock):
    """
    Test deletion of a bot when user is unauthorized.
    """
    controller = BotController(auth_service=mock_auth_service)
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException

    with pytest.raises(HTTPException) as exc_info:
        await controller.delete_bot(token="invalid_token", bot_id=1)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication failed"

@pytest.mark.asyncio
async def test_delete_bot_unauthorized_admin(mock_auth_service_admin: AsyncMock):
    """
    Test deletion of a bot when user is an admin but unauthorized for that endpoint.
    """
    controller = BotController(auth_service=mock_auth_service_admin)
    mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

    with pytest.raises(HTTPException) as exc_info:
         await controller.delete_bot(token="test_token", bot_id=1)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Authorization failed"