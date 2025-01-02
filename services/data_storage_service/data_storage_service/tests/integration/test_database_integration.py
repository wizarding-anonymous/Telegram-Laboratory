import pytest
import httpx
from src.config import settings
from src.integrations.auth_service import AuthService
from src.integrations.auth_service.client import get_current_user
from src.db.models import Bot

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
async def test_create_bot_success(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
    """
    Test that the bot is successfully created, including database schema creation.
    """
    mocker.patch("src.integrations.auth_service.AuthService", return_value = mock_auth_service)
    response = await client.post(
        "/bots/",
        headers={"Authorization": "Bearer test_token"},
        json={"name": "Test Bot", "description": "A test bot"}
    )
    assert response.status_code == 201
    assert "id" in response.json()
    assert "dsn" in response.json()

    bot_id = response.json()["id"]

    response = await client.get(
         f"/bots/{bot_id}",
          headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert "dsn" in response.json()

@pytest.mark.asyncio
async def test_get_all_bots_success(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
    """
    Test that all bots are successfully retrieved.
    """
    mocker.patch("src.integrations.auth_service.AuthService", return_value = mock_auth_service)
    # Create two bots first
    await client.post(
        "/bots/",
        headers={"Authorization": "Bearer test_token"},
        json={"name": "Test Bot 1", "description": "Test bot 1"}
    )
    await client.post(
        "/bots/",
        headers={"Authorization": "Bearer test_token"},
        json={"name": "Test Bot 2", "description": "Test bot 2"}
    )


    response = await client.get(
        "/bots/",
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)
    assert len(response.json()["items"]) >= 2

@pytest.mark.asyncio
async def test_update_bot_success(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
     """
    Test that the bot is successfully updated.
    """
     mocker.patch("src.integrations.auth_service.AuthService", return_value = mock_auth_service)

     # Create a bot first
     response = await client.post(
        "/bots/",
        headers={"Authorization": "Bearer test_token"},
        json={"name": "Test Bot", "description": "A test bot"}
     )
     assert response.status_code == 201
     bot_id = response.json()["id"]


     # Update the bot
     response = await client.put(
        f"/bots/{bot_id}",
        headers={"Authorization": "Bearer test_token"},
        json={"name": "Updated Bot Name", "description": "Updated Description"}
     )
     assert response.status_code == 200
     assert response.json()["name"] == "Updated Bot Name"
     assert response.json()["description"] == "Updated Description"

@pytest.mark.asyncio
async def test_delete_bot_success(client: httpx.AsyncClient, mock_auth_service: AuthService, mocker):
    """
    Test that the bot and its database are successfully deleted.
    """
    mocker.patch("src.integrations.auth_service.AuthService", return_value = mock_auth_service)

    # Create a bot first
    response = await client.post(
        "/bots/",
        headers={"Authorization": "Bearer test_token"},
        json={"name": "Test Bot", "description": "A test bot"}
    )
    assert response.status_code == 201
    bot_id = response.json()["id"]

    # Delete the bot
    response = await client.delete(
        f"/bots/{bot_id}",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Bot deleted successfully"

    # Try to retrieve, should fail
    response = await client.get(
        f"/bots/{bot_id}",
          headers={"Authorization": "Bearer test_token"}
     )
    assert response.status_code == 404