import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from src.integrations.auth_service import AuthService
from src.core.utils.exceptions import TelegramAPIException
from src.config import settings

@pytest.mark.asyncio
async def test_get_user_by_token_success():
    """Test successful user retrieval by token."""
    mock_client = AsyncMock()
    mock_client.get.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"id": 1, "email": "test@example.com", "roles": ["admin"]})
    )
    auth_service = AuthService(client=mock_client)
    user = await auth_service.get_user_by_token("test_token")
    assert user["id"] == 1
    assert user["email"] == "test@example.com"
    assert "admin" in user["roles"]


@pytest.mark.asyncio
async def test_get_user_by_token_http_error():
    """Test user retrieval with HTTP error."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = HTTPException(status_code=401, detail="Unauthorized")
    auth_service = AuthService(client=mock_client)
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_user_by_token("test_token")
    assert exc_info.value.status_code == 401
    assert "Unauthorized" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_user_by_token_unhandled_error():
    """Test user retrieval with unhandled error."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Unexpected error")
    auth_service = AuthService(client=mock_client)
    with pytest.raises(HTTPException) as exc_info:
         await auth_service.get_user_by_token("test_token")
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_user_roles_success():
    """Test getting user roles successfully."""
    mock_client = AsyncMock()
    mock_client.get.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value=["admin", "user"])
    )
    auth_service = AuthService(client=mock_client)
    roles = await auth_service.get_user_roles(user_id=1)
    assert roles == ["admin", "user"]
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_roles_http_error():
     """Test get user roles with HTTP error."""
     mock_client = AsyncMock()
     mock_client.get.side_effect = HTTPException(status_code=404, detail="User not found")
     auth_service = AuthService(client=mock_client)
     with pytest.raises(HTTPException) as exc_info:
         await auth_service.get_user_roles(user_id=1)
     assert exc_info.value.status_code == 404
     assert "User not found" in exc_info.value.detail
     mock_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_roles_unhandled_error():
     """Test get user roles with unhandled exception."""
     mock_client = AsyncMock()
     mock_client.get.side_effect = Exception("Unexpected error")
     auth_service = AuthService(client=mock_client)
     with pytest.raises(Exception) as exc_info:
        await auth_service.get_user_roles(user_id=1)
     assert "Unexpected error" in str(exc_info.value)
     mock_client.get.assert_called_once()