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
async def create_test_variable(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test variable in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO variables (block_id, name, value)
            VALUES (:block_id, :name, :value)
            RETURNING id, block_id, name, value, created_at;
            """
        )
        params = {
             "block_id": block_id,
            "name": "test_var",
            "value": "test_value"
        }
        result = await session.execute(query, params)
        await session.commit()
        variable = result.fetchone()
        return dict(variable._mapping)
    
@pytest.mark.asyncio
async def test_create_variable_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of variable.
    """
    block_id = create_test_block["id"]
    test_data = {
        "name": "test_var",
        "value": "test_value",
    }
    response = await client.post(
        f"/blocks/{block_id}/variables", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == test_data["name"]
    assert response_data["value"] == test_data["value"]
    assert response_data["block_id"] == block_id
    assert response_data["id"] is not None

@pytest.mark.asyncio
async def test_create_variable_route_not_found_block(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test creation of variable with not found block.
    """
    block_id = 999
    test_data = {
         "name": "test_var",
        "value": "test_value",
    }
    response = await client.post(
        f"/blocks/{block_id}/variables", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Block not found"


@pytest.mark.asyncio
async def test_get_variable_by_id_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful get variable by id.
    """
    variable_id = create_test_variable["id"]
    response = await client.get(
        f"/variables/{variable_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == variable_id
    assert response_data["name"] == create_test_variable["name"]
    assert response_data["value"] == create_test_variable["value"]
    assert response_data["block_id"] == create_test_variable["block_id"]
    assert response_data["type"] == "variable"

@pytest.mark.asyncio
async def test_get_variable_by_id_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
     Test get variable by id with not found variable.
    """
    variable_id = 999
    response = await client.get(
        f"/variables/{variable_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Variable not found"

@pytest.mark.asyncio
async def test_update_variable_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful update of variable.
    """
    variable_id = create_test_variable["id"]
    updated_data = {
        "name": "updated_test_var",
        "value": "updated_test_value",
    }
    response = await client.put(
        f"/variables/{variable_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == updated_data["name"]
    assert response_data["value"] == updated_data["value"]
    assert response_data["id"] == variable_id
    

@pytest.mark.asyncio
async def test_update_variable_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update variable with not found variable.
    """
    variable_id = 999
    updated_data = {
        "name": "updated_test_var",
        "value": "updated_test_value",
    }
    response = await client.put(
        f"/variables/{variable_id}", headers=get_auth_header, json=updated_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Variable not found"


@pytest.mark.asyncio
async def test_delete_variable_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful delete variable.
    """
    variable_id = create_test_variable["id"]
    response = await client.delete(
        f"/variables/{variable_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response = await client.get(
        f"/variables/{variable_id}", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_variable_route_not_found(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test delete variable with not found variable.
    """
    variable_id = 999
    response = await client.delete(
       f"/variables/{variable_id}", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Variable not found"


@pytest.mark.asyncio
async def test_assign_value_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful assign value route.
    """
    variable_id = create_test_variable["id"]
    test_data = {
        "value": "new_test_value",
    }
    response = await client.post(
        f"/variables/{variable_id}/assign", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Value assigned successfully"

@pytest.mark.asyncio
async def test_assign_value_route_not_found_variable(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test assign value route with not found variable.
    """
    variable_id = 999
    test_data = {
         "value": "new_test_value",
    }
    response = await client.post(
        f"/variables/{variable_id}/assign", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Variable not found"

@pytest.mark.asyncio
async def test_retrieve_value_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful retrieve value route.
    """
    variable_id = create_test_variable["id"]
    response = await client.get(
        f"/variables/{variable_id}/retrieve", headers=get_auth_header
    )
    assert response.status_code == 200
    assert response.json()["value"] == "test_value"

@pytest.mark.asyncio
async def test_retrieve_value_route_not_found_variable(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test retrieve value route with not found variable.
    """
    variable_id = 999
    response = await client.get(
        f"/variables/{variable_id}/retrieve", headers=get_auth_header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Variable not found"


@pytest.mark.asyncio
async def test_update_value_route_success(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful update value route.
    """
    variable_id = create_test_variable["id"]
    test_data = {
         "value": "updated_test_value",
    }
    response = await client.post(
       f"/variables/{variable_id}/update", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Value updated successfully"

@pytest.mark.asyncio
async def test_update_value_route_not_found_variable(
    client: httpx.AsyncClient,
    get_auth_header: Dict[str, str],
    mock_auth_service: AsyncMock,
):
    """
    Test update value route with not found variable.
    """
    variable_id = 999
    test_data = {
        "value": "updated_test_value",
    }
    response = await client.post(
        f"/variables/{variable_id}/update", headers=get_auth_header, json=test_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Variable not found"