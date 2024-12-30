import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings

@pytest.mark.asyncio
async def test_create_text_message(client: AsyncClient, get_auth_header: dict):
    """Test creating a new text message block."""
    test_message_data = {"content": "Test Message"}
    response = await client.post(
        "/bots/1/messages/", headers=get_auth_header, json=test_message_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["content"] == test_message_data["content"]
    assert data["type"] == "text"


@pytest.mark.asyncio
async def test_get_text_message_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a text message block by ID."""
    test_message_data = {"content": "Test Message"}
    create_response = await client.post(
         "/bots/1/messages/", headers=get_auth_header, json=test_message_data
    )
    assert create_response.status_code == 201
    created_message = create_response.json()
    message_id = created_message["id"]
    response = await client.get(
        f"/blocks/{message_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message_id
    assert data["content"] == test_message_data["content"]
    assert data["type"] == "text"



@pytest.mark.asyncio
async def test_get_all_text_messages(client: AsyncClient, get_auth_header: dict):
    """Test getting all text messages."""
    test_message_data1 = {"content": "Test Message 1"}
    test_message_data2 = {"content": "Test Message 2"}
    await client.post("/bots/1/messages/", headers=get_auth_header, json=test_message_data1)
    await client.post("/bots/1/messages/", headers=get_auth_header, json=test_message_data2)

    response = await client.get("/bots/1/messages/", headers=get_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    contents = [item["content"] for item in data]
    assert "Test Message 1" in contents
    assert "Test Message 2" in contents

@pytest.mark.asyncio
async def test_update_text_message(client: AsyncClient, get_auth_header: dict):
    """Test updating a text message block."""
    test_message_data = {"content": "Test Message"}
    create_response = await client.post(
        "/bots/1/messages/", headers=get_auth_header, json=test_message_data
    )
    assert create_response.status_code == 201
    created_message = create_response.json()
    message_id = created_message["id"]
    update_data = {"content": "Updated Message"}
    response = await client.put(
        f"/blocks/{message_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message_id
    assert data["content"] == update_data["content"]
    assert data["type"] == "text"

@pytest.mark.asyncio
async def test_delete_text_message(client: AsyncClient, get_auth_header: dict):
    """Test deleting a text message block."""
    test_message_data = {"content": "Test Message"}
    create_response = await client.post(
       "/bots/1/messages/", headers=get_auth_header, json=test_message_data
    )
    assert create_response.status_code == 201
    created_message = create_response.json()
    message_id = created_message["id"]
    response = await client.delete(
        f"/blocks/{message_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(f"/blocks/{message_id}", headers=get_auth_header)
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_text_message_unauthorized(client: AsyncClient):
    """Test creating a text message without authorization."""
    test_message_data = {"content": "Test Message"}
    response = await client.post("/bots/1/messages/", json=test_message_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_text_message_by_id_unauthorized(client: AsyncClient):
    """Test getting a text message by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_text_message_unauthorized(client: AsyncClient):
    """Test update a text message without authorization."""
    update_data = {"content": "Updated Message"}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_text_message_unauthorized(client: AsyncClient):
    """Test delete a text message without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_get_text_message_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a text message that does not exist."""
    response = await client.get(
       "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_update_text_message_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a text message that does not exist."""
    update_data = {"content": "Updated Message"}
    response = await client.put(
        "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_text_message_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a text message that does not exist."""
    response = await client.delete(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_text_message_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a text message with invalid bot id"""
    test_message_data = {"content": "Test Message", "bot_id": "invalid_id"}
    response = await client.post(
         "/bots/1/messages/", headers=get_auth_header, json=test_message_data
    )
    assert response.status_code == 400