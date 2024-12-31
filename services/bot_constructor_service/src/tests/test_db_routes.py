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
async def create_test_db_block(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test db block in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO databases (block_id, connection_params, query)
            VALUES (:block_id, :connection_params, :query)
            RETURNING id, block_id, connection_params, query, created_at;
            """
        )
        params = {
            "block_id": block_id,
            "connection_params": {"db_uri": "test_uri"},
            "query": "test_query",
        }
        result = await session.execute(query, params)
        await session.commit()
        db_block = result.fetchone()
        return dict(db_block._mapping)

@pytest.mark.asyncio
async def test_create_db_block_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of db block.
    """
    block_id = create_test_block["id"]
    test_data = {
        "connection_params": {"db_uri": "test_uri"},
        "query": "test_query"
    }
    response = await client.post(
        f"/blocks/{block_id}/databases", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["connection_params"] == test_data["connection_params"]
    assert response_data["query"] == test_data["query"]
    assert response_data["block_id"] == block_id
    assert response_data["id"] is not None


@pytest.mark.asyncio
async def test_create_db_block_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of db block with not found block.
    """
    block_id = 999
    test_data = {
         "connection_params": {"db_uri": "test_uri"},
        "query": "test_query"
    }
    response = await client.post(
        f"/blocks/{block_id}/databases", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"

@pytest.mark.asyncio
async def test_get_db_block_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful get db block by id.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.get(
      f"/databases/{db_block_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == db_block_id
    assert response_data["connection_params"] == create_test_db_block["connection_params"]
    assert response_data["query"] == create_test_db_block["query"]
    assert response_data["block_id"] == create_test_db_block["block_id"]

@pytest.mark.asyncio
async def test_get_db_block_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test get db block by id with not found db block.
    """
    db_block_id = 999
    response = await client.get(
        f"/databases/{db_block_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"


@pytest.mark.asyncio
async def test_update_db_block_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful update of db block.
    """
    db_block_id = create_test_db_block["id"]
    updated_data = {
        "connection_params": {"new_db_uri": "test_uri_updated"},
        "query": "updated_query"
    }
    response = await client.put(
        f"/databases/{db_block_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["connection_params"] == updated_data["connection_params"]
    assert response_data["query"] == updated_data["query"]


@pytest.mark.asyncio
async def test_update_db_block_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update db block with not found db block.
    """
    db_block_id = 999
    updated_data = {
        "connection_params": {"new_db_uri": "test_uri_updated"},
        "query": "updated_query"
    }
    response = await client.put(
        f"/databases/{db_block_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"

@pytest.mark.asyncio
async def test_delete_db_block_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful delete db block.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.delete(
        f"/databases/{db_block_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
        f"/databases/{db_block_id}", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_db_block_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test delete db block with not found db block.
    """
    db_block_id = 999
    response = await client.delete(
        f"/databases/{db_block_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"

@pytest.mark.asyncio
async def test_db_connect_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful db connect route.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.post(
        f"/databases/{db_block_id}/connect", headers=get_auth_header
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Database connected successfully"

@pytest.mark.asyncio
async def test_db_connect_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test db connect route with not found block.
    """
    db_block_id = 999
    response = await client.post(
        f"/databases/{db_block_id}/connect", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"

@pytest.mark.asyncio
async def test_db_query_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful db query route.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.post(
        f"/databases/{db_block_id}/query", headers=get_auth_header
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Database query executed successfully"


@pytest.mark.asyncio
async def test_db_query_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test db query route with not found block.
    """
    db_block_id = 999
    response = await client.post(
        f"/databases/{db_block_id}/query", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"


@pytest.mark.asyncio
async def test_db_fetch_data_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful db fetch data route.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.post(
        f"/databases/{db_block_id}/fetch", headers=get_auth_header
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Data fetched successfully"


@pytest.mark.asyncio
async def test_db_fetch_data_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test db fetch data route with not found block.
    """
    db_block_id = 999
    response = await client.post(
        f"/databases/{db_block_id}/fetch", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"


@pytest.mark.asyncio
async def test_db_insert_data_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful db insert data route.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.post(
        f"/databases/{db_block_id}/insert", headers=get_auth_header
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Data inserted successfully"


@pytest.mark.asyncio
async def test_db_insert_data_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test db insert data route with not found block.
    """
    db_block_id = 999
    response = await client.post(
       f"/databases/{db_block_id}/insert", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"

@pytest.mark.asyncio
async def test_db_update_data_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful db update data route.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.post(
        f"/databases/{db_block_id}/update", headers=get_auth_header
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Data updated successfully"


@pytest.mark.asyncio
async def test_db_update_data_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test db update data route with not found block.
    """
    db_block_id = 999
    response = await client.post(
        f"/databases/{db_block_id}/update", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"

@pytest.mark.asyncio
async def test_db_delete_data_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_db_block: Dict[str, Any]
):
    """
    Test successful db delete data route.
    """
    db_block_id = create_test_db_block["id"]
    response = await client.post(
       f"/databases/{db_block_id}/delete", headers=get_auth_header
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Data deleted successfully"

@pytest.mark.asyncio
async def test_db_delete_data_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test db delete data route with not found block.
    """
    db_block_id = 999
    response = await client.post(
       f"/databases/{db_block_id}/delete", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Database block not found"