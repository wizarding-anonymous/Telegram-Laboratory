import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_bot(client: AsyncClient, get_auth_header: dict):
    """Test creating a new bot."""
    test_bot_data = {"name": "Test Bot", "description": "Test Description"}
    response = await client.post(
        "/bots/", headers=get_auth_header, json=test_bot_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == test_bot_data["name"]
    assert data["description"] == test_bot_data["description"]


@pytest.mark.asyncio
async def test_get_bot_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting bot by ID."""
    test_bot_data = {"name": "Test Bot", "description": "Test Description"}
    create_response = await client.post(
        "/bots/", headers=get_auth_header, json=test_bot_data
    )
    assert create_response.status_code == 201
    created_bot = create_response.json()
    bot_id = created_bot["id"]
    response = await client.get(
        f"/bots/{bot_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bot_id
    assert data["name"] == test_bot_data["name"]
    assert data["description"] == test_bot_data["description"]


@pytest.mark.asyncio
async def test_get_all_bots(client: AsyncClient, get_auth_header: dict):
    """Test getting all bots."""
    test_bot_data1 = {"name": "Test Bot 1", "description": "Test Description 1"}
    test_bot_data2 = {"name": "Test Bot 2", "description": "Test Description 2"}
    await client.post("/bots/", headers=get_auth_header, json=test_bot_data1)
    await client.post("/bots/", headers=get_auth_header, json=test_bot_data2)

    response = await client.get("/bots/", headers=get_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    names = [item["name"] for item in data]
    assert "Test Bot 1" in names
    assert "Test Bot 2" in names

@pytest.mark.asyncio
async def test_update_bot(client: AsyncClient, get_auth_header: dict):
    """Test updating a bot."""
    test_bot_data = {"name": "Test Bot", "description": "Test Description"}
    create_response = await client.post(
        "/bots/", headers=get_auth_header, json=test_bot_data
    )
    assert create_response.status_code == 201
    created_bot = create_response.json()
    bot_id = created_bot["id"]
    update_data = {"name": "Updated Bot", "description": "Updated Description"}
    response = await client.put(
        f"/bots/{bot_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bot_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

@pytest.mark.asyncio
async def test_delete_bot(client: AsyncClient, get_auth_header: dict):
    """Test deleting a bot."""
    test_bot_data = {"name": "Test Bot", "description": "Test Description"}
    create_response = await client.post(
        "/bots/", headers=get_auth_header, json=test_bot_data
    )
    assert create_response.status_code == 201
    created_bot = create_response.json()
    bot_id = created_bot["id"]
    response = await client.delete(
        f"/bots/{bot_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(f"/bots/{bot_id}", headers=get_auth_header)
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_bot_unauthorized(client: AsyncClient):
    """Test creating a bot without authorization."""
    test_bot_data = {"name": "Test Bot", "description": "Test Description"}
    response = await client.post("/bots/", json=test_bot_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_bot_by_id_unauthorized(client: AsyncClient):
    """Test getting a bot by id without authorization."""
    response = await client.get("/bots/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_bot_unauthorized(client: AsyncClient):
    """Test update a bot without authorization."""
    update_data = {"name": "Updated Bot", "description": "Updated Description"}
    response = await client.put("/bots/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_bot_unauthorized(client: AsyncClient):
    """Test delete a bot without authorization."""
    response = await client.delete("/bots/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_bot_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a bot that does not exist."""
    response = await client.get(
        "/bots/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_bot_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a bot that does not exist."""
    update_data = {"name": "Updated Bot", "description": "Updated Description"}
    response = await client.put(
        "/bots/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete_bot_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a bot that does not exist."""
    response = await client.delete(
        "/bots/999", headers=get_auth_header
    )
    assert response.status_code == 404