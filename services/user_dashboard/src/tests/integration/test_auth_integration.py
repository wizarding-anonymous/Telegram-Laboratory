import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from src.integrations.auth_service import AuthService
from src.core.utils.exceptions import AuthenticationException

@pytest.mark.asyncio
async def test_auth_middleware_success(client: AsyncClient, get_auth_header: dict[str, str], mock_auth_service: AsyncMock):
    """
    Test successful authentication with valid token and user role.
    """
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}

    response = await client.get("/test-auth", headers=get_auth_header)
    assert response.status_code == 200
    assert response.json() == {"message": "Authenticated"}


@pytest.mark.asyncio
async def test_auth_middleware_failure_invalid_token(client: AsyncClient, mock_auth_service: AsyncMock):
    """
    Test authentication failure with invalid token.
    """
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException
    response = await client.get("/test-auth", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed"}


@pytest.mark.asyncio
async def test_auth_middleware_failure_no_token(client: AsyncClient, mock_auth_service: AsyncMock):
    """
    Test authentication failure with no token provided.
    """
    mock_auth_service.get_user_by_token.side_effect = AuthenticationException
    response = await client.get("/test-auth")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed"}

@pytest.mark.asyncio
async def test_auth_middleware_failure_unauthorized_role(client: AsyncClient, get_auth_header: dict[str, str], mock_auth_service_admin: AsyncMock):
    """
    Test authentication failure when user has unauthorized role
    """
    mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

    response = await client.get("/test-auth-admin", headers=get_auth_header)
    assert response.status_code == 403
    assert response.json() == {"detail": "Authorization failed"}


@pytest.mark.asyncio
async def test_auth_middleware_success_admin_role(client: AsyncClient, get_auth_header: dict[str, str], mock_auth_service_admin: AsyncMock):
     """
     Test successful authentication when user has admin role
     """
     mock_auth_service_admin.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     response = await client.get("/test-auth-admin-access", headers=get_auth_header)
     assert response.status_code == 200
     assert response.json() == {"message": "Admin authenticated"}