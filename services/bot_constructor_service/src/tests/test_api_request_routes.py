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
async def create_test_api_request(create_test_bot) -> Dict[str, Any]:
    """
    Fixture to create a test api_request in the database.
    """
    bot_id = create_test_bot["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO api_requests (bot_id, url, method, headers, params, body)
            VALUES (:bot_id, :url, :method, :headers, :params, :body)
            RETURNING id, bot_id, url, method, headers, params, body, created_at;
        """
        )
        params = {
            "bot_id": bot_id,
            "url": "https://test.com",
            "method": "GET",
            "headers": {"Content-Type": "application/json"},
            "params": {"test_param": "test_value"},
            "body": None,
        }
        result = await session.execute(query, params)
        await session.commit()
        api_request = result.fetchone()
        return dict(api_request._mapping)


@pytest.mark.asyncio
async def test_create_api_request_route(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any],
):
    """
    Test successful creation of api request.
    """
    bot_id = create_test_bot["id"]
    test_data = {
        "url": "https://test.com",
        "method": "GET",
        "headers": {"Content-Type": "application/json"},
        "params": {"test_param": "test_value"},
        "body": None,
    }

    response = await client.post(
        f"/bots/{bot_id}/api-requests",
        headers=get_auth_header,
        json=test_data,
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["type"] == "api_request"
    assert response_data["url"] == test_data["url"]
    assert response_data["method"] == test_data["method"]
    assert response_data["headers"] == test_data["headers"]
    assert response_data["params"] == test_data["params"]
    assert response_data["body"] == test_data["body"]


@pytest.mark.asyncio
async def test_create_api_request_route_not_found_bot(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of api request with not found bot.
    """
    bot_id = 999
    test_data = {
        "url": "https://test.com",
        "method": "GET",
        "headers": {"Content-Type": "application/json"},
        "params": {"test_param": "test_value"},
        "body": None,
    }
    response = await client.post(
        f"/bots/{bot_id}/api-requests",
        headers=get_auth_header,
        json=test_data,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Bot not found"

@pytest.mark.asyncio
async def test_get_api_request_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_api_request: Dict[str, Any]
):
    """
    Test successful get api request by id.
    """
    api_request_id = create_test_api_request["id"]
    response = await client.get(
        f"/api-requests/{api_request_id}",
        headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == api_request_id
    assert response_data["type"] == "api_request"
    assert response_data["url"] == create_test_api_request["url"]
    assert response_data["method"] == create_test_api_request["method"]
    assert response_data["headers"] == create_test_api_request["headers"]
    assert response_data["params"] == create_test_api_request["params"]
    assert response_data["body"] == create_test_api_request["body"]


@pytest.mark.asyncio
async def test_get_api_request_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
    Test get api request by id with not found api_request.
    """
    api_request_id = 999
    response = await client.get(
        f"/api-requests/{api_request_id}",
        headers=get_auth_header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Api request not found"


@pytest.mark.asyncio
async def test_update_api_request_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_api_request: Dict[str, Any]
):
    """
    Test successful update of api request.
    """
    api_request_id = create_test_api_request["id"]
    updated_data = {
        "url": "https://test2.com",
        "method": "POST",
        "headers": {"Content-Type": "application/xml"},
        "params": {"test_param": "test_value_2"},
        "body": {"key": "test"},
    }
    response = await client.put(
        f"/api-requests/{api_request_id}",
        headers=get_auth_header,
        json=updated_data,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["url"] == updated_data["url"]
    assert response_data["method"] == updated_data["method"]
    assert response_data["headers"] == updated_data["headers"]
    assert response_data["params"] == updated_data["params"]
    assert response_data["body"] == updated_data["body"]


@pytest.mark.asyncio
async def test_update_api_request_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update api request with not found api_request.
    """
    api_request_id = 999
    updated_data = {
        "url": "https://test2.com",
        "method": "POST",
        "headers": {"Content-Type": "application/xml"},
        "params": {"test_param": "test_value_2"},
        "body": {"key": "test"},
    }
    response = await client.put(
        f"/api-requests/{api_request_id}",
        headers=get_auth_header,
        json=updated_data,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Api request not found"


@pytest.mark.asyncio
async def test_delete_api_request_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_api_request: Dict[str, Any]
):
    """
    Test successful delete api request.
    """
    api_request_id = create_test_api_request["id"]
    response = await client.delete(
        f"/api-requests/{api_request_id}",
        headers=get_auth_header,
    )
    assert response.status_code == 204

    response = await client.get(
      f"/api-requests/{api_request_id}",
       headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_api_request_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
    Test delete api request with not found api_request.
    """
    api_request_id = 999
    response = await client.delete(
        f"/api-requests/{api_request_id}",
        headers=get_auth_header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Api request not found"


@pytest.mark.asyncio
async def test_process_api_request_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_api_request: Dict[str, Any]
):
    """
    Test successful process api request.
    """
    api_request_id = create_test_api_request["id"]
    test_data_process = {
        "api_request_id": api_request_id,
        "chat_id": 123,
         "template_context":  {"test_var": "test_value_from_user"}
    }
    response = await client.post(
        f"/api-requests/{api_request_id}/process",
        headers=get_auth_header,
        json=test_data_process
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Api request processed successfully"


@pytest.mark.asyncio
async def test_process_api_request_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
):
    """
     Test process api request with not found api_request.
    """
    api_request_id = 999
    test_data_process = {
        "api_request_id": api_request_id,
        "chat_id": 123,
         "template_context":  {"test_var": "test_value_from_user"}
    }
    response = await client.post(
        f"/api-requests/{api_request_id}/process",
        headers=get_auth_header,
         json=test_data_process
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Api request not found"