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
async def create_test_flow(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test flow in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO flows (block_id, logic)
            VALUES (:block_id, :logic)
            RETURNING id, block_id, logic, created_at;
            """
        )
        params = {
            "block_id": block_id,
            "logic": {"start": block_id, "next_blocks": {str(block_id): [block_id]}},
        }
        result = await session.execute(query, params)
        await session.commit()
        flow = result.fetchone()
        return dict(flow._mapping)

@pytest.mark.asyncio
async def test_create_flow_chart_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of flow chart.
    """
    block_id = create_test_block["id"]
    test_data = {
       "logic": {"start": block_id, "next_blocks": {str(block_id): [block_id]}}
    }
    response = await client.post(
        f"/blocks/{block_id}/flow", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["logic"] == test_data["logic"]
    assert response_data["block_id"] == block_id
    assert response_data["type"] == "flow"
    assert response_data["id"] is not None


@pytest.mark.asyncio
async def test_create_flow_chart_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of flow chart with not found block.
    """
    block_id = 999
    test_data = {
        "logic": {"start": block_id, "next_blocks": {str(block_id): [block_id]}}
    }
    response = await client.post(
        f"/blocks/{block_id}/flow", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"

@pytest.mark.asyncio
async def test_get_flow_chart_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_flow: Dict[str, Any]
):
    """
    Test successful get flow chart by id.
    """
    flow_id = create_test_flow["id"]
    response = await client.get(
        f"/flow/{flow_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == flow_id
    assert response_data["logic"] == create_test_flow["logic"]
    assert response_data["block_id"] == create_test_flow["block_id"]
    assert response_data["type"] == "flow"


@pytest.mark.asyncio
async def test_get_flow_chart_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test get flow chart by id with not found flow chart.
    """
    flow_id = 999
    response = await client.get(
       f"/flow/{flow_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Flow chart not found"

@pytest.mark.asyncio
async def test_update_flow_chart_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_flow: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful update of flow chart.
    """
    flow_id = create_test_flow["id"]
    block_id = create_test_block["id"]
    updated_data = {
         "logic": {"start": block_id, "next_blocks": {str(block_id): [block_id, block_id]}}
    }
    response = await client.put(
        f"/flow/{flow_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["logic"] == updated_data["logic"]
    assert response_data["id"] == flow_id

@pytest.mark.asyncio
async def test_update_flow_chart_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
     create_test_block: Dict[str, Any]
):
    """
    Test update flow chart with not found flow chart.
    """
    flow_id = 999
    block_id = create_test_block["id"]
    updated_data = {
         "logic": {"start": block_id, "next_blocks": {str(block_id): [block_id]}}
    }
    response = await client.put(
        f"/flow/{flow_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Flow chart not found"

@pytest.mark.asyncio
async def test_delete_flow_chart_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_flow: Dict[str, Any]
):
    """
    Test successful delete flow chart.
    """
    flow_id = create_test_flow["id"]
    response = await client.delete(
        f"/flow/{flow_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response = await client.get(
      f"/flow/{flow_id}", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_flow_chart_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
     Test delete flow chart with not found flow chart.
    """
    flow_id = 999
    response = await client.delete(
        f"/flow/{flow_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Flow chart not found"

@pytest.mark.asyncio
async def test_process_flow_chart_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_flow: Dict[str, Any]
):
    """
    Test successful process flow chart.
    """
    flow_id = create_test_flow["id"]
    test_data = {
        "flow_id": flow_id,
        "chat_id": 123,
    }
    response = await client.post(
        f"/flow/{flow_id}/process", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Flow chart processed successfully"

@pytest.mark.asyncio
async def test_process_flow_chart_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test process flow chart with not found flow chart.
    """
    flow_id = 999
    test_data = {
        "flow_id": flow_id,
        "chat_id": 123,
    }
    response = await client.post(
        f"/flow/{flow_id}/process", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Flow chart not found"