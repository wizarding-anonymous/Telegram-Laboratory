import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_database(client: AsyncClient, get_auth_header: dict):
    """Test creating a new database block."""
    test_database_data = {"query": "SELECT * FROM users;"}
    response = await client.post(
        "/bots/1/db/", headers=get_auth_header, json=test_database_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["query"] == test_database_data["query"]
    assert data["type"] == "database_connect"


@pytest.mark.asyncio
async def test_get_database_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a database block by ID."""
    test_database_data = {"query": "SELECT * FROM users;"}
    create_response = await client.post(
        "/bots/1/db/", headers=get_auth_header, json=test_database_data
    )
    assert create_response.status_code == 201
    created_database = create_response.json()
    database_id = created_database["id"]
    response = await client.get(
        f"/blocks/{database_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == database_id
    assert data["query"] == test_database_data["query"]
    assert data["type"] == "database_connect"


@pytest.mark.asyncio
async def test_update_database(client: AsyncClient, get_auth_header: dict):
    """Test updating a database block."""
    test_database_data = {"query": "SELECT * FROM users;"}
    create_response = await client.post(
        "/bots/1/db/", headers=get_auth_header, json=test_database_data
    )
    assert create_response.status_code == 201
    created_database = create_response.json()
    database_id = created_database["id"]
    update_data = {"query": "SELECT * FROM test_users;"}
    response = await client.put(
        f"/blocks/{database_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == database_id
    assert data["query"] == update_data["query"]


@pytest.mark.asyncio
async def test_delete_database(client: AsyncClient, get_auth_header: dict):
    """Test deleting a database block."""
    test_database_data = {"query": "SELECT * FROM users;"}
    create_response = await client.post(
        "/bots/1/db/", headers=get_auth_header, json=test_database_data
    )
    assert create_response.status_code == 201
    created_database = create_response.json()
    database_id = created_database["id"]
    response = await client.delete(
        f"/blocks/{database_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response_get = await client.get(
        f"/blocks/{database_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404
    

@pytest.mark.asyncio
async def test_create_database_unauthorized(client: AsyncClient):
    """Test creating a database without authorization."""
    test_database_data = {"query": "SELECT * FROM users;"}
    response = await client.post("/bots/1/db/", json=test_database_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_database_by_id_unauthorized(client: AsyncClient):
    """Test getting a database by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_database_unauthorized(client: AsyncClient):
    """Test update a database without authorization."""
    update_data = {"query": "SELECT * FROM test_users;"}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_database_unauthorized(client: AsyncClient):
    """Test delete a database without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_get_database_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a database that does not exist."""
    response = await client.get(
       "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_database_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a database that does not exist."""
    update_data = {"query": "SELECT * FROM test_users;"}
    response = await client.put(
        "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete_database_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a database that does not exist."""
    response = await client.delete(
         "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_database_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a database with invalid bot id"""
    test_database_data = {"query": "SELECT * FROM users;", "bot_id": "invalid_id"}
    response = await client.post(
         "/bots/1/db/", headers=get_auth_header, json=test_database_data
    )
    assert response.status_code == 400