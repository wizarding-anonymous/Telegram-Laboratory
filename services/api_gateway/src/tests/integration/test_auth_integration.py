import pytest
import httpx
from src.config import settings
from src.integrations.auth_service_client import AuthService

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_auth_service(mocker) -> AuthService:
    """
    Fixture to create a mock AuthService.
    """
    mock = mocker.AsyncMock(spec=AuthService)
    mock.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    return mock


@pytest.mark.asyncio
async def test_auth_middleware_success(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
    """
    Test that the auth middleware correctly verifies a token and returns user data.
    """
    mocker.patch("src.integrations.auth_service_client.AuthService", return_value = mock_auth_service)
    response = await client.get(
        "/gateway/routes/", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_middleware_missing_token(client: httpx.AsyncClient):
    """
    Test that the auth middleware returns an error if no token is provided.
    """
    response = await client.get(
        "/gateway/routes/"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header is missing or malformed"


@pytest.mark.asyncio
async def test_auth_middleware_invalid_token(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
    """
    Test that the auth middleware returns an error if an invalid token is provided.
    """
    mock_auth_service.get_user_by_token.return_value = None
    mocker.patch("src.integrations.auth_service_client.AuthService", return_value = mock_auth_service)

    response = await client.get(
        "/gateway/routes/", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@pytest.mark.asyncio
async def test_admin_middleware_success(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
    """
    Test that the admin middleware allows access for an admin user.
    """
    mocker.patch("src.integrations.auth_service_client.AuthService", return_value = mock_auth_service)
    response = await client.post(
        "/gateway/routes/", headers={"Authorization": "Bearer test_token"}, json={"path": "/test", "method": "GET", "destination_url": "http://test", "auth_required": True}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_admin_middleware_non_admin(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
    """
    Test that the admin middleware returns an error for a non-admin user.
    """
    mock_auth_service.get_user_by_token.return_value = {"id": 2, "roles": ["user"]}
    mocker.patch("src.integrations.auth_service_client.AuthService", return_value = mock_auth_service)
    response = await client.post(
         "/gateway/routes/", headers={"Authorization": "Bearer test_token"}, json={"path": "/test", "method": "GET", "destination_url": "http://test", "auth_required": True}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Required roles: ['admin']"