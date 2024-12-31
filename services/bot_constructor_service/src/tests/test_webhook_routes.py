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
async def create_test_webhook(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test webhook in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
         query = text(
            """
            INSERT INTO webhooks (block_id, url)
            VALUES (:block_id, :url)
            RETURNING id, block_id, url, created_at;
            """
        )
         params = {"block_id": block_id, "url": "test_url"}
         result = await session.execute(query, params)
         await session.commit()
         webhook = result.fetchone()
         return dict(webhook._mapping)


@pytest.mark.asyncio
async def test_create_webhook_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of webhook.
    """
    block_id = create_test_block["id"]
    test_data = {
        "url": "test_url",
    }
    response = await client.post(
        f"/blocks/{block_id}/webhooks", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["url"] == test_data["url"]
    assert response_data["block_id"] == block_id
    assert response_data["type"] == "webhook"
    assert response_data["id"] is not None


@pytest.mark.asyncio
async def test_create_webhook_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of webhook with not found block.
    """
    block_id = 999
    test_data = {
         "url": "test_url",
    }
    response = await client.post(
        f"/blocks/{block_id}/webhooks", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_get_webhook_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_webhook: Dict[str, Any]
):
    """
    Test successful get webhook by id.
    """
    webhook_id = create_test_webhook["id"]
    response = await client.get(
        f"/webhooks/{webhook_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == webhook_id
    assert response_data["url"] == create_test_webhook["url"]
    assert response_data["block_id"] == create_test_webhook["block_id"]
    assert response_data["type"] == "webhook"


@pytest.mark.asyncio
async def test_get_webhook_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test get webhook by id with not found webhook.
    """
    webhook_id = 999
    response = await client.get(
        f"/webhooks/{webhook_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook not found"

@pytest.mark.asyncio
async def test_update_webhook_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_webhook: Dict[str, Any]
):
    """
    Test successful update of webhook.
    """
    webhook_id = create_test_webhook["id"]
    updated_data = {
        "url": "new_test_url",
    }
    response = await client.put(
        f"/webhooks/{webhook_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["url"] == updated_data["url"]
    assert response_data["id"] == webhook_id


@pytest.mark.asyncio
async def test_update_webhook_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update webhook with not found webhook.
    """
    webhook_id = 999
    updated_data = {
        "url": "new_test_url",
    }
    response = await client.put(
        f"/webhooks/{webhook_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook not found"


@pytest.mark.asyncio
async def test_delete_webhook_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_webhook: Dict[str, Any]
):
    """
    Test successful delete webhook.
    """
    webhook_id = create_test_webhook["id"]
    response = await client.delete(
        f"/webhooks/{webhook_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
        f"/webhooks/{webhook_id}", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_webhook_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test delete webhook with not found webhook.
    """
    webhook_id = 999
    response = await client.delete(
        f"/webhooks/{webhook_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook not found"

@pytest.mark.asyncio
async def test_set_webhook_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_webhook: Dict[str, Any]
):
    """
    Test successful set webhook route.
    """
    webhook_id = create_test_webhook["id"]
    test_data = {}
    response = await client.post(
        f"/webhooks/{webhook_id}/set", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Webhook set successfully"

@pytest.mark.asyncio
async def test_set_webhook_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test set webhook route with not found block.
    """
    webhook_id = 999
    test_data = {}
    response = await client.post(
        f"/webhooks/{webhook_id}/set", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook not found"

@pytest.mark.asyncio
async def test_delete_webhook_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_webhook: Dict[str, Any]
):
    """
    Test successful delete webhook route.
    """
    webhook_id = create_test_webhook["id"]
    test_data = {}
    response = await client.post(
        f"/webhooks/{webhook_id}/delete", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Webhook deleted successfully"

@pytest.mark.asyncio
async def test_delete_webhook_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test delete webhook route with not found block.
    """
    webhook_id = 999
    test_data = {}
    response = await client.post(
        f"/webhooks/{webhook_id}/delete", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook not found"