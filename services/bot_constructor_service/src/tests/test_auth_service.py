import pytest
import httpx
from unittest.mock import AsyncMock
from src.integrations.auth_service import AuthService
from src.config import settings
from typing import Dict, Any

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
def get_auth_header() -> Dict[str, str]:
    """
    Fixture to get authorization header.
    """
    return {"Authorization": f"Bearer test_token"}

@pytest.fixture(scope="session")
async def client():
    """
    Fixture to create httpx client with app.
    """
    from src.app import app
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock(spec=AuthService)
    return mock


@pytest.mark.asyncio
async def test_auth_middleware_success(
    client: httpx.AsyncClient, mock_auth_service: AsyncMock, get_auth_header: Dict[str,str]
):
    """
    Test successful authentication.
    """
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

    response = await client.get("/health", headers=get_auth_header)

    assert response.status_code == 200
    mock_auth_service.get_user_by_token.assert_called_once()



@pytest.mark.asyncio
async def test_auth_middleware_unauthorized(
    client: httpx.AsyncClient, mock_auth_service: AsyncMock
):
    """
    Test unauthorized access without token.
    """
    mock_auth_service.get_user_by_token.return_value = None

    response = await client.get("/health")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    mock_auth_service.get_user_by_token.assert_not_called()



@pytest.mark.asyncio
async def test_auth_middleware_invalid_token(
    client: httpx.AsyncClient, mock_auth_service: AsyncMock
):
    """
     Test authentication with invalid token.
    """
    mock_auth_service.get_user_by_token.return_value = None

    response = await client.get(
      "/health", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    mock_auth_service.get_user_by_token.assert_called_once()

@pytest.mark.asyncio
async def test_get_current_user_success(
    client: httpx.AsyncClient, mock_auth_service: AsyncMock, get_auth_header: Dict[str,str]
):
    """
      Test successful getting current user.
    """
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

    response = await client.get("/auth/me", headers=get_auth_header)
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["roles"] == ["admin"]
    mock_auth_service.get_user_by_token.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(
    client: httpx.AsyncClient, mock_auth_service: AsyncMock
):
    """
    Test getting current user with unauthorized access.
    """
    mock_auth_service.get_user_by_token.return_value = None

    response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    mock_auth_service.get_user_by_token.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(
    client: httpx.AsyncClient, mock_auth_service: AsyncMock
):
    """
     Test getting current user with invalid token.
    """
    mock_auth_service.get_user_by_token.return_value = None

    response = await client.get(
      "/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    mock_auth_service.get_user_by_token.assert_called_once()