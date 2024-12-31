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


@pytest.fixture
async def create_test_bot_settings(create_test_bot) -> Dict[str, Any]:
    """
    Fixture to create test bot settings in the database.
    """
    bot_id = create_test_bot["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO bot_settings (bot_id, token, library)
            VALUES (:bot_id, :token, :library)
            RETURNING id, bot_id, token, library;
        """
        )
        params = {
            "bot_id": bot_id,
            "token": "test_token",
            "library": "telegram_api",
        }
        result = await session.execute(query, params)
        await session.commit()
        bot_settings = result.fetchone()
        return dict(bot_settings._mapping)


@pytest.mark.asyncio
async def test_create_bot_settings_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any],
):
    """
    Test successful creation of bot settings.
    """
    bot_id = create_test_bot["id"]
    test_data = {
        "token": "test_token",
        "library": "telegram_api",
    }
    response = await client.post(
        f"/bots/{bot_id}/settings", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["token"] == test_data["token"]
    assert response_data["library"] == test_data["library"]
    assert response_data["id"] is not None


@pytest.mark.asyncio
async def test_create_bot_settings_route_not_found_bot(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of bot settings with not found bot.
    """
    bot_id = 999
    test_data = {
        "token": "test_token",
        "library": "telegram_api",
    }
    response = await client.post(
        f"/bots/{bot_id}/settings", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot not found"


@pytest.mark.asyncio
async def test_get_bot_settings_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot_settings: Dict[str, Any],
):
    """
    Test successful get bot settings by id.
    """
    bot_settings_id = create_test_bot_settings["id"]
    response = await client.get(
        f"/bot-settings/{bot_settings_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == bot_settings_id
    assert response_data["token"] == create_test_bot_settings["token"]
    assert response_data["library"] == create_test_bot_settings["library"]
    assert response_data["id"] is not None


@pytest.mark.asyncio
async def test_get_bot_settings_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test get bot settings by id with not found bot settings.
    """
    bot_settings_id = 999
    response = await client.get(
        f"/bot-settings/{bot_settings_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot settings not found"


@pytest.mark.asyncio
async def test_update_bot_settings_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot_settings: Dict[str, Any],
):
    """
    Test successful update of bot settings.
    """
    bot_settings_id = create_test_bot_settings["id"]
    updated_data = {
        "token": "new_test_token",
        "library": "aiogram",
    }
    response = await client.put(
        f"/bot-settings/{bot_settings_id}",
        headers=get_auth_header,
        json=updated_data,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["token"] == updated_data["token"]
    assert response_data["library"] == updated_data["library"]
    assert response_data["id"] == bot_settings_id


@pytest.mark.asyncio
async def test_update_bot_settings_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update bot settings with not found bot settings.
    """
    bot_settings_id = 999
    updated_data = {
        "token": "new_test_token",
        "library": "aiogram",
    }
    response = await client.put(
        f"/bot-settings/{bot_settings_id}",
        headers=get_auth_header,
        json=updated_data,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot settings not found"


@pytest.mark.asyncio
async def test_delete_bot_settings_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot_settings: Dict[str, Any],
):
    """
    Test successful delete bot settings.
    """
    bot_settings_id = create_test_bot_settings["id"]
    response = await client.delete(
        f"/bot-settings/{bot_settings_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
      f"/bot-settings/{bot_settings_id}", headers=get_auth_header
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_bot_settings_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test delete bot settings with not found bot settings.
    """
    bot_settings_id = 999
    response = await client.delete(
        f"/bot-settings/{bot_settings_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot settings not found"