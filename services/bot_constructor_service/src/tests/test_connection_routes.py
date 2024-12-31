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
async def create_test_connection(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test connection in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO connections (source_block_id, target_block_id)
            VALUES (:source_block_id, :target_block_id)
            RETURNING id, source_block_id, target_block_id, type;
            """
        )
        params = {"source_block_id": block_id, "target_block_id": block_id}
        result = await session.execute(query, params)
        await session.commit()
        connection = result.fetchone()
        return dict(connection._mapping)


@pytest.mark.asyncio
async def test_create_connection_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of connection.
    """
    block_id = create_test_block["id"]
    test_data = {
        "source_block_id": block_id,
        "target_block_id": block_id,
    }
    response = await client.post(
        "/blocks/connections", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["source_block_id"] == test_data["source_block_id"]
    assert response_data["target_block_id"] == test_data["target_block_id"]
    assert "id" in response_data

@pytest.mark.asyncio
async def test_create_connection_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test creation of connection with not found block.
    """
    block_id = 999
    test_data = {
         "source_block_id": block_id,
        "target_block_id": block_id,
    }
    response = await client.post(
        "/blocks/connections", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Source block not found"

@pytest.mark.asyncio
async def test_get_connection_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_connection: Dict[str, Any]
):
    """
    Test successful get connection by id.
    """
    connection_id = create_test_connection["id"]
    response = await client.get(
        f"/connections/{connection_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == connection_id
    assert response_data["source_block_id"] == create_test_connection["source_block_id"]
    assert response_data["target_block_id"] == create_test_connection["target_block_id"]


@pytest.mark.asyncio
async def test_get_connection_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test get connection by id with not found connection.
    """
    connection_id = 999
    response = await client.get(
        f"/connections/{connection_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Connection not found"

@pytest.mark.asyncio
async def test_update_connection_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_connection: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful update of connection.
    """
    connection_id = create_test_connection["id"]
    block_id = create_test_block["id"]
    updated_data = {
        "source_block_id": block_id,
        "target_block_id": block_id,
          "type": "test_type"
    }
    response = await client.put(
        f"/connections/{connection_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["source_block_id"] == updated_data["source_block_id"]
    assert response_data["target_block_id"] == updated_data["target_block_id"]
    assert response_data["type"] == updated_data["type"]

@pytest.mark.asyncio
async def test_update_connection_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
     create_test_block: Dict[str, Any]
):
    """
    Test update connection with not found connection.
    """
    connection_id = 999
    block_id = create_test_block["id"]
    updated_data = {
         "source_block_id": block_id,
        "target_block_id": block_id,
         "type": "test_type"
    }
    response = await client.put(
        f"/connections/{connection_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Connection not found"


@pytest.mark.asyncio
async def test_delete_connection_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_connection: Dict[str, Any]
):
    """
    Test successful delete connection.
    """
    connection_id = create_test_connection["id"]
    response = await client.delete(
        f"/connections/{connection_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response = await client.get(
      f"/connections/{connection_id}", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_connection_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
    Test delete connection with not found connection.
    """
    connection_id = 999
    response = await client.delete(
        f"/connections/{connection_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Connection not found"