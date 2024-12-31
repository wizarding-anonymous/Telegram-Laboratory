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
async def create_test_block(create_test_bot) -> Dict[str, Any]:
    """
    Fixture to create a test block in the database.
    """
    bot_id = create_test_bot["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO blocks (bot_id, type, content)
            VALUES (:bot_id, :type, :content)
            RETURNING id, bot_id, type, content, created_at;
        """
        )
        params = {"bot_id": bot_id, "type": "message", "content": {"text": "Test message"}}
        result = await session.execute(query, params)
        await session.commit()
        block = result.fetchone()
        return dict(block._mapping)


@pytest.mark.asyncio
async def test_create_block_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any]
):
    """
    Test successful creation of block.
    """
    bot_id = create_test_bot["id"]
    test_data = {
        "type": "message",
        "content": {"text": "Test message"},
    }
    response = await client.post(
        f"/bots/{bot_id}/blocks", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["type"] == test_data["type"]
    assert response_data["content"] == test_data["content"]
    assert response_data["bot_id"] == bot_id

@pytest.mark.asyncio
async def test_create_block_route_not_found_bot(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of block with not found bot.
    """
    bot_id = 999
    test_data = {
        "type": "message",
        "content": {"text": "Test message"},
    }
    response = await client.post(
        f"/bots/{bot_id}/blocks", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot not found"


@pytest.mark.asyncio
async def test_get_block_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful get block by id.
    """
    block_id = create_test_block["id"]
    response = await client.get(
      f"/blocks/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == block_id
    assert response_data["type"] == create_test_block["type"]
    assert response_data["content"] == create_test_block["content"]
    assert response_data["bot_id"] == create_test_block["bot_id"]


@pytest.mark.asyncio
async def test_get_block_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
     Test get block by id with not found block.
    """
    block_id = 999
    response = await client.get(
      f"/blocks/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_update_block_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful update of block.
    """
    block_id = create_test_block["id"]
    updated_data = {
        "type": "photo",
        "content": {"url": "test_url"},
    }
    response = await client.put(
        f"/blocks/{block_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["type"] == updated_data["type"]
    assert response_data["content"] == updated_data["content"]


@pytest.mark.asyncio
async def test_update_block_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test update block with not found block.
    """
    block_id = 999
    updated_data = {
        "type": "photo",
        "content": {"url": "test_url"},
    }
    response = await client.put(
        f"/blocks/{block_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"

@pytest.mark.asyncio
async def test_delete_block_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful delete block.
    """
    block_id = create_test_block["id"]
    response = await client.delete(
      f"/blocks/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
      f"/blocks/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_block_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
    Test delete block with not found block.
    """
    block_id = 999
    response = await client.delete(
      f"/blocks/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"