import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_connection(client: AsyncClient, get_auth_header: dict):
    """Test creating a new connection between blocks."""
    test_connection_data = {
        "source_block_id": 1,
        "target_block_id": 2,
        "type": "default"
    }
    response = await client.post(
       "/bots/1/connections/", headers=get_auth_header, json=test_connection_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["source_block_id"] == test_connection_data["source_block_id"]
    assert data["target_block_id"] == test_connection_data["target_block_id"]
    assert data["type"] == test_connection_data["type"]


@pytest.mark.asyncio
async def test_get_connection_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting connection by ID."""
    test_connection_data = {
        "source_block_id": 1,
        "target_block_id": 2,
        "type": "default"
    }
    create_response = await client.post(
       "/bots/1/connections/", headers=get_auth_header, json=test_connection_data
    )
    assert create_response.status_code == 201
    created_connection = create_response.json()
    connection_id = created_connection["id"]
    response = await client.get(
        f"/bots/1/connections/{connection_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == connection_id
    assert data["source_block_id"] == test_connection_data["source_block_id"]
    assert data["target_block_id"] == test_connection_data["target_block_id"]
    assert data["type"] == test_connection_data["type"]
    

@pytest.mark.asyncio
async def test_update_connection(client: AsyncClient, get_auth_header: dict):
    """Test updating a connection."""
    test_connection_data = {
         "source_block_id": 1,
        "target_block_id": 2,
        "type": "default"
    }
    create_response = await client.post(
         "/bots/1/connections/", headers=get_auth_header, json=test_connection_data
    )
    assert create_response.status_code == 201
    created_connection = create_response.json()
    connection_id = created_connection["id"]
    update_data = {"type": "updated_type",  "source_block_id": 3}
    response = await client.put(
        f"/bots/1/connections/{connection_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == connection_id
    assert data["type"] == update_data["type"]
    assert data["source_block_id"] == update_data["source_block_id"]
    assert data["target_block_id"] == test_connection_data["target_block_id"]

@pytest.mark.asyncio
async def test_delete_connection(client: AsyncClient, get_auth_header: dict):
    """Test deleting a connection."""
    test_connection_data = {
        "source_block_id": 1,
        "target_block_id": 2,
         "type": "default"
    }
    create_response = await client.post(
         "/bots/1/connections/", headers=get_auth_header, json=test_connection_data
    )
    assert create_response.status_code == 201
    created_connection = create_response.json()
    connection_id = created_connection["id"]
    response = await client.delete(
        f"/bots/1/connections/{connection_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(
        f"/bots/1/connections/{connection_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_connection_unauthorized(client: AsyncClient):
    """Test creating a connection without authorization."""
    test_connection_data = {"source_block_id": 1, "target_block_id": 2}
    response = await client.post("/bots/1/connections/", json=test_connection_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_connection_by_id_unauthorized(client: AsyncClient):
    """Test getting a connection by id without authorization."""
    response = await client.get("/bots/1/connections/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_connection_unauthorized(client: AsyncClient):
    """Test update a connection without authorization."""
    update_data = {"type": "updated_type"}
    response = await client.put("/bots/1/connections/1", json=update_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_connection_unauthorized(client: AsyncClient):
    """Test delete a connection without authorization."""
    response = await client.delete("/bots/1/connections/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_connection_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a connection that does not exist."""
    response = await client.get(
        "/bots/1/connections/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_connection_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a connection that does not exist."""
    update_data = {"type": "updated_type"}
    response = await client.put(
        "/bots/1/connections/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete_connection_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a connection that does not exist."""
    response = await client.delete(
        "/bots/1/connections/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_connection_with_invalid_block_ids(client: AsyncClient, get_auth_header: dict):
    """Test creating a connection with invalid block ids."""
    test_connection_data = {
        "source_block_id": -1,
        "target_block_id": 0,
        "type": "default"
    }
    response = await client.post(
        "/bots/1/connections/", headers=get_auth_header, json=test_connection_data
    )
    assert response.status_code == 400