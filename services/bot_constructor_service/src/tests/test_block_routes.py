import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_block(client: AsyncClient, get_auth_header: dict):
    """Test creating a new block."""
    test_block_data = {
        "bot_id": 1,
        "type": "text_message",
        "content": {"text": "Test Message"},
        "connections": [],
    }
    response = await client.post(
        "/bots/1/blocks/", headers=get_auth_header, json=test_block_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["type"] == test_block_data["type"]
    assert data["content"] == test_block_data["content"]
    assert data["connections"] == []


@pytest.mark.asyncio
async def test_get_block_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a block by ID."""
    test_block_data = {
        "bot_id": 1,
        "type": "text_message",
        "content": {"text": "Test Message"},
        "connections": [],
    }
    create_response = await client.post(
        "/bots/1/blocks/", headers=get_auth_header, json=test_block_data
    )
    assert create_response.status_code == 201
    created_block = create_response.json()
    block_id = created_block["id"]
    response = await client.get(
        f"/blocks/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == block_id
    assert data["type"] == test_block_data["type"]
    assert data["content"] == test_block_data["content"]
    assert data["connections"] == []


@pytest.mark.asyncio
async def test_get_all_blocks(client: AsyncClient, get_auth_header: dict):
    """Test getting all blocks."""
    test_block_data1 = {
        "bot_id": 1,
        "type": "text_message",
        "content": {"text": "Test Message 1"},
        "connections": [],
    }
    test_block_data2 = {
        "bot_id": 1,
        "type": "keyboard",
        "content": {"buttons": [["button1"]]},
         "connections": [],
    }
    await client.post("/bots/1/blocks/", headers=get_auth_header, json=test_block_data1)
    await client.post("/bots/1/blocks/", headers=get_auth_header, json=test_block_data2)
    response = await client.get(f"/bots/1/blocks/", headers=get_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    types = [item["type"] for item in data]
    assert "text_message" in types
    assert "keyboard" in types


@pytest.mark.asyncio
async def test_update_block(client: AsyncClient, get_auth_header: dict):
    """Test updating a block."""
    test_block_data = {
        "bot_id": 1,
        "type": "text_message",
        "content": {"text": "Test Message"},
        "connections": [],
    }
    create_response = await client.post(
        "/bots/1/blocks/", headers=get_auth_header, json=test_block_data
    )
    assert create_response.status_code == 201
    created_block = create_response.json()
    block_id = created_block["id"]
    update_data = {"content": {"text": "Updated Message"}, "connections": [10]}
    response = await client.put(
        f"/blocks/{block_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == block_id
    assert data["content"] == update_data["content"]
    assert data["connections"] == update_data["connections"]


@pytest.mark.asyncio
async def test_delete_block(client: AsyncClient, get_auth_header: dict):
    """Test deleting a block."""
    test_block_data = {
        "bot_id": 1,
        "type": "text_message",
        "content": {"text": "Test Message"},
         "connections": [],
    }
    create_response = await client.post(
        "/bots/1/blocks/", headers=get_auth_header, json=test_block_data
    )
    assert create_response.status_code == 201
    created_block = create_response.json()
    block_id = created_block["id"]
    response = await client.delete(
        f"/blocks/{block_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(f"/blocks/{block_id}", headers=get_auth_header)
    assert response_get.status_code == 404

@pytest.mark.asyncio
async def test_create_block_unauthorized(client: AsyncClient):
    """Test creating a block without authorization."""
    test_block_data = {
         "bot_id": 1,
        "type": "text_message",
        "content": {"text": "Test Message"},
         "connections": [],
    }
    response = await client.post("/blocks/", json=test_block_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_block_by_id_unauthorized(client: AsyncClient):
    """Test getting a block by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_block_unauthorized(client: AsyncClient):
    """Test updating a block without authorization."""
    update_data = {"content": {"text": "Updated Message"}, "connections": [10]}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_block_unauthorized(client: AsyncClient):
    """Test deleting a block without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_block_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a block that does not exist."""
    response = await client.get(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_block_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a block that does not exist."""
    update_data = {"content": {"text": "Updated Message"}, "connections": [10]}
    response = await client.put(
        "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete_block_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a block that does not exist."""
    response = await client.delete(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_create_block_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a block with invalid bot_id"""
    test_block_data = {
        "bot_id": "invalid_id",
        "type": "text_message",
        "content": {"text": "Test Message"},
        "connections": [],
    }
    response = await client.post(
         "/bots/1/blocks/", headers=get_auth_header, json=test_block_data
    )
    assert response.status_code == 400