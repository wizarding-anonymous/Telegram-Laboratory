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
async def test_create_message_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of message block.
    """
    block_id = create_test_block["id"]
    test_data = {
        "content": "Test message",
    }
    response = await client.post(
        f"/blocks/{block_id}/messages", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["content"] == test_data["content"]
    assert response_data["block_id"] == block_id
    assert response_data["type"] == "message"
    assert response_data["id"] is not None

@pytest.mark.asyncio
async def test_create_message_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of message block with not found block.
    """
    block_id = 999
    test_data = {
         "content": "Test message",
    }
    response = await client.post(
        f"/blocks/{block_id}/messages", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_get_message_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful get message block by id.
    """
    block_id = create_test_block["id"]
    response = await client.get(
        f"/messages/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == block_id
    assert response_data["content"] == create_test_block["content"]["text"]
    assert response_data["block_id"] == create_test_block["id"]
    assert response_data["type"] == "message"

@pytest.mark.asyncio
async def test_get_message_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test get message block by id with not found message block.
    """
    block_id = 999
    response = await client.get(
        f"/messages/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Message block not found"

@pytest.mark.asyncio
async def test_update_message_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful update of message block.
    """
    block_id = create_test_block["id"]
    updated_data = {
        "content": "Updated test message",
    }
    response = await client.put(
        f"/messages/{block_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["content"] == updated_data["content"]
    assert response_data["id"] == block_id

@pytest.mark.asyncio
async def test_update_message_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update message block with not found message block.
    """
    block_id = 999
    updated_data = {
        "content": "Updated test message",
    }
    response = await client.put(
        f"/messages/{block_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Message block not found"

@pytest.mark.asyncio
async def test_delete_message_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful delete message block.
    """
    block_id = create_test_block["id"]
    response = await client.delete(
      f"/messages/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
        f"/messages/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_message_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test delete message block with not found message block.
    """
    block_id = 999
    response = await client.delete(
       f"/messages/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Message block not found"

@pytest.mark.asyncio
async def test_send_text_message_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
     Test successful send text message route.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/messages/{block_id}/send", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Message sent successfully"

@pytest.mark.asyncio
async def test_send_text_message_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test send text message route with not found block.
    """
    block_id = 999
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/messages/{block_id}/send", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Message block not found"