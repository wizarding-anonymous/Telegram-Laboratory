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
async def test_get_chat_members_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful get chat members.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/members", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Chat members retrieved successfully"


@pytest.mark.asyncio
async def test_get_chat_members_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test get chat members with not found block.
    """
    block_id = 999
    test_data = {
         "chat_id": 123,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/members", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"

@pytest.mark.asyncio
async def test_ban_user_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful ban user.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
        "user_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/ban", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User banned successfully"


@pytest.mark.asyncio
async def test_ban_user_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test ban user with not found block.
    """
    block_id = 999
    test_data = {
         "chat_id": 123,
        "user_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/ban", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_unban_user_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful unban user.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
        "user_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/unban", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User unbanned successfully"


@pytest.mark.asyncio
async def test_unban_user_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test unban user with not found block.
    """
    block_id = 999
    test_data = {
        "chat_id": 123,
        "user_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/unban", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_set_chat_title_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful set chat title.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
        "title": "New Title",
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/title", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Chat title updated successfully"


@pytest.mark.asyncio
async def test_set_chat_title_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test set chat title with not found block.
    """
    block_id = 999
    test_data = {
         "chat_id": 123,
        "title": "New Title",
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/title", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_set_chat_description_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful set chat description.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
        "description": "New Description",
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/description", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Chat description updated successfully"


@pytest.mark.asyncio
async def test_set_chat_description_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test set chat description with not found block.
    """
    block_id = 999
    test_data = {
        "chat_id": 123,
        "description": "New Description",
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/description", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_pin_chat_message_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful pin chat message.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
        "message_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/pin", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Message pinned successfully"

@pytest.mark.asyncio
async def test_pin_chat_message_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test pin chat message with not found block.
    """
    block_id = 999
    test_data = {
        "chat_id": 123,
        "message_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/pin", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"

@pytest.mark.asyncio
async def test_unpin_chat_message_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful unpin chat message.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
        "message_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/unpin", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Message unpinned successfully"


@pytest.mark.asyncio
async def test_unpin_chat_message_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test unpin chat message with not found block.
    """
    block_id = 999
    test_data = {
        "chat_id": 123,
        "message_id": 456,
    }
    response = await client.post(
        f"/blocks/{block_id}/chat/unpin", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"