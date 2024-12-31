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
async def create_test_media_group(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test media group in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO media_groups (block_id, items)
            VALUES (:block_id, :items)
            RETURNING id, block_id, items, created_at;
            """
        )
        params = {
            "block_id": block_id,
            "items": [
                {"type": "photo", "media": "test_photo_url"},
                {"type": "video", "media": "test_video_url"},
            ],
        }
        result = await session.execute(query, params)
        await session.commit()
        media_group = result.fetchone()
        return dict(media_group._mapping)


@pytest.mark.asyncio
async def test_create_media_group_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of media group.
    """
    block_id = create_test_block["id"]
    test_data = {
        "items": [
            {"type": "photo", "media": "test_photo_url"},
            {"type": "video", "media": "test_video_url"},
        ],
    }
    response = await client.post(
        f"/blocks/{block_id}/media-groups", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["items"] == test_data["items"]
    assert response_data["block_id"] == block_id
    assert response_data["type"] == "media_group"
    assert response_data["id"] is not None


@pytest.mark.asyncio
async def test_create_media_group_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of media group with not found block.
    """
    block_id = 999
    test_data = {
         "items": [
            {"type": "photo", "media": "test_photo_url"},
            {"type": "video", "media": "test_video_url"},
        ],
    }
    response = await client.post(
        f"/blocks/{block_id}/media-groups", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_get_media_group_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_media_group: Dict[str, Any]
):
    """
    Test successful get media group by id.
    """
    media_group_id = create_test_media_group["id"]
    response = await client.get(
        f"/media-groups/{media_group_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == media_group_id
    assert response_data["items"] == create_test_media_group["items"]
    assert response_data["block_id"] == create_test_media_group["block_id"]
    assert response_data["type"] == "media_group"


@pytest.mark.asyncio
async def test_get_media_group_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test get media group by id with not found media group.
    """
    media_group_id = 999
    response = await client.get(
        f"/media-groups/{media_group_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Media group not found"

@pytest.mark.asyncio
async def test_update_media_group_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_media_group: Dict[str, Any]
):
    """
    Test successful update of media group.
    """
    media_group_id = create_test_media_group["id"]
    updated_data = {
        "items": [
            {"type": "audio", "media": "test_audio_url"},
            {"type": "document", "media": "test_document_url"},
        ],
    }
    response = await client.put(
        f"/media-groups/{media_group_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["items"] == updated_data["items"]
    assert response_data["id"] == media_group_id


@pytest.mark.asyncio
async def test_update_media_group_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update media group with not found media group.
    """
    media_group_id = 999
    updated_data = {
        "items": [
            {"type": "audio", "media": "test_audio_url"},
            {"type": "document", "media": "test_document_url"},
        ],
    }
    response = await client.put(
        f"/media-groups/{media_group_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Media group not found"

@pytest.mark.asyncio
async def test_delete_media_group_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_media_group: Dict[str, Any]
):
    """
    Test successful delete media group.
    """
    media_group_id = create_test_media_group["id"]
    response = await client.delete(
       f"/media-groups/{media_group_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
        f"/media-groups/{media_group_id}", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_media_group_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test delete media group with not found media group.
    """
    media_group_id = 999
    response = await client.delete(
       f"/media-groups/{media_group_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Media group not found"


@pytest.mark.asyncio
async def test_send_media_group_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_media_group: Dict[str, Any]
):
    """
    Test successful send media group route.
    """
    media_group_id = create_test_media_group["id"]
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/media-groups/{media_group_id}/send", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Media group sent successfully"

@pytest.mark.asyncio
async def test_send_media_group_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test send media group route with not found block.
    """
    media_group_id = 999
    test_data = {
        "chat_id": 123,
    }
    response = await client.post(
        f"/media-groups/{media_group_id}/send", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Media group not found"