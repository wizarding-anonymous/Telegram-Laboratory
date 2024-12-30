import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_variable(client: AsyncClient, get_auth_header: dict):
    """Test creating a new variable block."""
    test_variable_data = {"name": "test_var", "value": "test_value"}
    response = await client.post(
        "/bots/1/variables/", headers=get_auth_header, json=test_variable_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == test_variable_data["name"]
    assert data["value"] == test_variable_data["value"]
    assert data["type"] == "variable"


@pytest.mark.asyncio
async def test_get_variable_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a variable block by ID."""
    test_variable_data = {"name": "test_var", "value": "test_value"}
    create_response = await client.post(
       "/bots/1/variables/", headers=get_auth_header, json=test_variable_data
    )
    assert create_response.status_code == 201
    created_variable = create_response.json()
    variable_id = created_variable["id"]
    response = await client.get(
        f"/blocks/{variable_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == variable_id
    assert data["name"] == test_variable_data["name"]
    assert data["value"] == test_variable_data["value"]
    assert data["type"] == "variable"


@pytest.mark.asyncio
async def test_update_variable(client: AsyncClient, get_auth_header: dict):
    """Test updating a variable block."""
    test_variable_data = {"name": "test_var", "value": "test_value"}
    create_response = await client.post(
        "/bots/1/variables/", headers=get_auth_header, json=test_variable_data
    )
    assert create_response.status_code == 201
    created_variable = create_response.json()
    variable_id = created_variable["id"]
    update_data = {"value": "updated_value"}
    response = await client.put(
        f"/blocks/{variable_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == variable_id
    assert data["value"] == update_data["value"]


@pytest.mark.asyncio
async def test_delete_variable(client: AsyncClient, get_auth_header: dict):
    """Test deleting a variable block."""
    test_variable_data = {"name": "test_var", "value": "test_value"}
    create_response = await client.post(
        "/bots/1/variables/", headers=get_auth_header, json=test_variable_data
    )
    assert create_response.status_code == 201
    created_variable = create_response.json()
    variable_id = created_variable["id"]
    response = await client.delete(
        f"/blocks/{variable_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(
        f"/blocks/{variable_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404

@pytest.mark.asyncio
async def test_create_variable_unauthorized(client: AsyncClient):
    """Test creating a variable without authorization."""
    test_variable_data = {"name": "test_var", "value": "test_value"}
    response = await client.post("/bots/1/variables/", json=test_variable_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_variable_by_id_unauthorized(client: AsyncClient):
    """Test getting a variable by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_variable_unauthorized(client: AsyncClient):
    """Test update a variable without authorization."""
    update_data = {"value": "updated_value"}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_variable_unauthorized(client: AsyncClient):
    """Test delete a variable without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_variable_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a variable that does not exist."""
    response = await client.get(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_variable_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a variable that does not exist."""
    update_data = {"value": "updated_value"}
    response = await client.put(
        "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_variable_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a variable that does not exist."""
    response = await client.delete(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_create_variable_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a variable with invalid bot id."""
    test_variable_data = {"name": "test_var", "value": "test_value", "bot_id": "invalid_id"}
    response = await client.post(
         "/bots/1/variables/", headers=get_auth_header, json=test_variable_data
    )
    assert response.status_code == 400