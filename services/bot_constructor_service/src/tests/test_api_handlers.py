import pytest
import httpx
from typing import Dict, Any
from unittest.mock import AsyncMock
from src.app import app
from src.config import settings
from src.integrations.auth_service import AuthService
from src.db import get_session, close_engine
from sqlalchemy import text
from src.core.utils.exceptions import ObjectNotFoundException
from src.core.logic_manager.handlers import api_handlers
from src.integrations.telegram import TelegramAPI
from src.integrations.redis_client import redis_client


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
def mock_telegram_api() -> AsyncMock:
    """
    Fixture to create a mock TelegramAPI client.
    """
    mock = AsyncMock(spec=TelegramAPI)
    mock.send_message.return_value = {"ok": True}
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
async def test_make_api_request_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any],
    mock_telegram_api: AsyncMock
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
async def test_make_api_request_not_found_bot(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    mock_telegram_api: AsyncMock
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
async def test_update_api_request_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any]
):
    """
    Test successful update of api request.
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

    api_request_id = response.json()["id"]
    
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
async def test_update_api_request_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock
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
async def test_delete_api_request_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
     create_test_bot: Dict[str, Any]
):
    """
    Test successful delete api request.
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
    api_request_id = response.json()["id"]
    
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
async def test_delete_api_request_not_found(
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
async def test_process_api_request_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    mock_telegram_api: AsyncMock,
    create_test_bot: Dict[str, Any]
):
        """
        Test processing api request.
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
        api_request_id = response.json()["id"]

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
async def test_process_api_request_not_found_api_request(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
        """
        Test processing api request not found api_request.
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


@pytest.mark.asyncio
async def test_process_api_request_not_valid_method(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_bot: Dict[str, Any]
):
        """
        Test processing api request.
        """
        bot_id = create_test_bot["id"]
        test_data = {
            "url": "https://test.com",
            "method": "TEST",
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
        api_request_id = response.json()["id"]

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
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid method for api request"

@pytest.mark.asyncio
async def test_process_api_request_fail(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    mock_telegram_api: AsyncMock,
     create_test_bot: Dict[str, Any]
):
        """
        Test processing api request.
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
        api_request_id = response.json()["id"]
        mock_telegram_api.send_message.side_effect = Exception('Test exception')

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
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error: Test exception"