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


@pytest.fixture
async def create_test_keyboard(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test keyboard in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO keyboards (block_id, buttons, type)
            VALUES (:block_id, :buttons, :type)
            RETURNING id, block_id, buttons, type, created_at;
            """
        )
        params = {"block_id": block_id, "buttons": [{"text": "test"}], "type": "reply"}
        result = await session.execute(query, params)
        await session.commit()
        keyboard = result.fetchone()
        return dict(keyboard._mapping)

@pytest.mark.asyncio
async def test_create_keyboard_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of keyboard.
    """
    block_id = create_test_block["id"]
    test_data = {
        "buttons": [{"text": "test"}],
        "type": "reply",
    }
    response = await client.post(
        f"/blocks/{block_id}/keyboards", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["buttons"] == test_data["buttons"]
    assert response_data["type"] == test_data["type"]
    assert response_data["block_id"] == block_id
    assert response_data["id"] is not None

@pytest.mark.asyncio
async def test_create_keyboard_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test creation of keyboard with not found block.
    """
    block_id = 999
    test_data = {
        "buttons": [{"text": "test"}],
        "type": "reply",
    }
    response = await client.post(
        f"/blocks/{block_id}/keyboards", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"

@pytest.mark.asyncio
async def test_get_keyboard_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_keyboard: Dict[str, Any]
):
    """
    Test successful get keyboard by id.
    """
    keyboard_id = create_test_keyboard["id"]
    response = await client.get(
        f"/keyboards/{keyboard_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == keyboard_id
    assert response_data["buttons"] == create_test_keyboard["buttons"]
    assert response_data["type"] == create_test_keyboard["type"]
    assert response_data["block_id"] == create_test_keyboard["block_id"]

@pytest.mark.asyncio
async def test_get_keyboard_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
    Test get keyboard by id with not found keyboard.
    """
    keyboard_id = 999
    response = await client.get(
        f"/keyboards/{keyboard_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Keyboard not found"

@pytest.mark.asyncio
async def test_update_keyboard_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_keyboard: Dict[str, Any]
):
    """
    Test successful update of keyboard.
    """
    keyboard_id = create_test_keyboard["id"]
    updated_data = {
        "buttons": [{"text": "test_updated"}],
        "type": "inline",
    }
    response = await client.put(
        f"/keyboards/{keyboard_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["buttons"] == updated_data["buttons"]
    assert response_data["type"] == updated_data["type"]
    assert response_data["id"] == keyboard_id

@pytest.mark.asyncio
async def test_update_keyboard_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update keyboard with not found keyboard.
    """
    keyboard_id = 999
    updated_data = {
        "buttons": [{"text": "test_updated"}],
         "type": "inline",
    }
    response = await client.put(
        f"/keyboards/{keyboard_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Keyboard not found"


@pytest.mark.asyncio
async def test_delete_keyboard_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_keyboard: Dict[str, Any]
):
    """
    Test successful delete keyboard.
    """
    keyboard_id = create_test_keyboard["id"]
    response = await client.delete(
        f"/keyboards/{keyboard_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
      f"/keyboards/{keyboard_id}", headers=get_auth_header
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_keyboard_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test delete keyboard with not found keyboard.
    """
    keyboard_id = 999
    response = await client.delete(
        f"/keyboards/{keyboard_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Keyboard not found"

@pytest.mark.asyncio
async def test_create_reply_keyboard_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
     create_test_block: Dict[str, Any]
):
    """
    Test successful create reply keyboard route.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/blocks/{block_id}/keyboards/reply", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Reply keyboard created successfully"

@pytest.mark.asyncio
async def test_create_reply_keyboard_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test create reply keyboard route with not found block.
    """
    block_id = 999
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
         f"/blocks/{block_id}/keyboards/reply", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Keyboard not found"

@pytest.mark.asyncio
async def test_create_inline_keyboard_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
     create_test_block: Dict[str, Any]
):
    """
     Test successful create inline keyboard route.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/blocks/{block_id}/keyboards/inline", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Inline keyboard created successfully"
    

@pytest.mark.asyncio
async def test_create_inline_keyboard_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test create inline keyboard route with not found block.
    """
    block_id = 999
    test_data = {
         "chat_id": 123,
    }
    response = await client.post(
       f"/blocks/{block_id}/keyboards/inline", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Keyboard not found"


@pytest.mark.asyncio
async def test_remove_keyboard_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful remove keyboard route.
    """
    block_id = create_test_block["id"]
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/blocks/{block_id}/keyboards/remove", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Keyboard removed successfully"


@pytest.mark.asyncio
async def test_remove_keyboard_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test remove keyboard route with not found block.
    """
    block_id = 999
    test_data = {
         "chat_id": 123,
    }
    response = await client.post(
        f"/blocks/{block_id}/keyboards/remove", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"