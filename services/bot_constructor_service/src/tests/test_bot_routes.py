import pytest
import httpx
from typing import Dict, Any
from unittest.mock import AsyncMock
from src.config import settings
from src.integrations.auth_service import AuthService
from src.db import get_session, close_engine
from sqlalchemy import text


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
    await close_engine()


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock(spec=AuthService)
    mock.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    return mock


@pytest.fixture
async def create_test_bot(mock_auth_service) -> Dict[str, Any]:
    """
    Fixture to create a test bot in the database.
    """
    async with get_session() as session:
        query = text(
            """
            INSERT INTO bots (user_id, name)
            VALUES (:user_id, :name)
            RETURNING id, user_id, name, created_at;
        """
        )
        params = {"user_id": 1, "name": "Test Bot"}
        result = await session.execute(query, params)
        await session.commit()
        bot = result.fetchone()
        return dict(bot._mapping)


@pytest.mark.asyncio
async def test_create_bot_route_success(
    client: httpx.AsyncClient, get_auth_header: Dict[str, str], mock_auth_service: AsyncMock
):
    """
    Test successful creation of a bot.
    """
    test_data = {
        "name": "Test Bot 2",
    }
    response = await client.post("/bots/", headers=get_auth_header, json=test_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == test_data["name"]
    assert "id" in response_data
    assert "created_at" in response_data

@pytest.mark.asyncio
async def test_get_bot_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any]
):
    """
    Test successful get bot by id.
    """
    bot_id = create_test_bot["id"]
    response = await client.get(f"/bots/{bot_id}", headers=get_auth_header)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == bot_id
    assert response_data["name"] == create_test_bot["name"]
    assert response_data["user_id"] == create_test_bot["user_id"]
    assert "created_at" in response_data


@pytest.mark.asyncio
async def test_get_bot_by_id_not_found(
    client: httpx.AsyncClient, get_auth_header: Dict[str, str], mock_auth_service: AsyncMock
):
    """
     Test get bot by id with not found bot.
    """
    bot_id = 999
    response = await client.get(f"/bots/{bot_id}", headers=get_auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot not found"


@pytest.mark.asyncio
async def test_update_bot_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any]
):
    """
    Test successful update of a bot.
    """
    bot_id = create_test_bot["id"]
    updated_data = {
        "name": "Updated Test Bot",
    }
    response = await client.put(
        f"/bots/{bot_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == updated_data["name"]
    assert "updated_at" in response_data


@pytest.mark.asyncio
async def test_update_bot_route_not_found(
    client: httpx.AsyncClient, get_auth_header: Dict[str, str], mock_auth_service: AsyncMock
):
    """
    Test update bot with not found bot.
    """
    bot_id = 999
    updated_data = {
        "name": "Updated Test Bot",
    }
    response = await client.put(
        f"/bots/{bot_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot not found"

@pytest.mark.asyncio
async def test_delete_bot_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any]
):
    """
    Test successful delete bot.
    """
    bot_id = create_test_bot["id"]
    response = await client.delete(f"/bots/{bot_id}", headers=get_auth_header)
    assert response.status_code == 204

    response = await client.get(f"/bots/{bot_id}", headers=get_auth_header)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_bot_route_not_found(
    client: httpx.AsyncClient, get_auth_header: Dict[str, str], mock_auth_service: AsyncMock
):
    """
     Test delete bot with not found bot.
    """
    bot_id = 999
    response = await client.delete(f"/bots/{bot_id}", headers=get_auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot not found"