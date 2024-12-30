import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_callback(client: AsyncClient, get_auth_header: dict):
    """Test creating a new callback query block."""
    test_callback_data = {"data": "test_callback_data"}
    response = await client.post(
        "/bots/1/callbacks/", headers=get_auth_header, json=test_callback_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["data"] == test_callback_data["data"]
    assert data["type"] == "handle_callback_query"


@pytest.mark.asyncio
async def test_get_callback_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a callback block by ID."""
    test_callback_data = {"data": "test_callback_data"}
    create_response = await client.post(
         "/bots/1/callbacks/", headers=get_auth_header, json=test_callback_data
    )
    assert create_response.status_code == 201
    created_callback = create_response.json()
    callback_id = created_callback["id"]
    response = await client.get(
        f"/blocks/{callback_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == callback_id
    assert data["data"] == test_callback_data["data"]
    assert data["type"] == "handle_callback_query"


@pytest.mark.asyncio
async def test_update_callback(client: AsyncClient, get_auth_header: dict):
    """Test updating a callback block."""
    test_callback_data = {"data": "test_callback_data"}
    create_response = await client.post(
         "/bots/1/callbacks/", headers=get_auth_header, json=test_callback_data
    )
    assert create_response.status_code == 201
    created_callback = create_response.json()
    callback_id = created_callback["id"]
    update_data = {"data": "updated_callback_data"}
    response = await client.put(
        f"/blocks/{callback_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == callback_id
    assert data["data"] == update_data["data"]


@pytest.mark.asyncio
async def test_delete_callback(client: AsyncClient, get_auth_header: dict):
    """Test deleting a callback block."""
    test_callback_data = {"data": "test_callback_data"}
    create_response = await client.post(
         "/bots/1/callbacks/", headers=get_auth_header, json=test_callback_data
    )
    assert create_response.status_code == 201
    created_callback = create_response.json()
    callback_id = created_callback["id"]
    response = await client.delete(
        f"/blocks/{callback_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(
        f"/blocks/{callback_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_callback_unauthorized(client: AsyncClient):
    """Test creating a callback without authorization."""
    test_callback_data = {"data": "test_callback_data"}
    response = await client.post("/bots/1/callbacks/", json=test_callback_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_callback_by_id_unauthorized(client: AsyncClient):
    """Test getting a callback by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_callback_unauthorized(client: AsyncClient):
    """Test update a callback without authorization."""
    update_data = {"data": "updated_callback_data"}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_callback_unauthorized(client: AsyncClient):
    """Test delete a callback without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401
    

@pytest.mark.asyncio
async def test_get_callback_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a callback that does not exist."""
    response = await client.get(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_callback_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a callback that does not exist."""
    update_data = {"data": "updated_callback_data"}
    response = await client.put(
        "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete_callback_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a callback that does not exist."""
    response = await client.delete(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_create_callback_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a callback with invalid bot_id"""
    test_callback_data = {"data": "test_callback_data", "bot_id": "invalid_id"}
    response = await client.post(
         "/bots/1/callbacks/", headers=get_auth_header, json=test_callback_data
    )
    assert response.status_code == 400