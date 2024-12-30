import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings

@pytest.mark.asyncio
async def test_update_chat_title(client: AsyncClient, get_auth_header: dict):
    """Test updating a chat title."""
    test_chat_data = {
        "chat_id": 123456,
        "title": "Test Chat Title",
    }
    response = await client.put(
        "/bots/1/chats/title", headers=get_auth_header, json=test_chat_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Chat title updated successfully"

@pytest.mark.asyncio
async def test_update_chat_description(client: AsyncClient, get_auth_header: dict):
    """Test updating a chat description."""
    test_chat_data = {
        "chat_id": 123456,
        "description": "Test Description",
    }
    response = await client.put(
         "/bots/1/chats/description", headers=get_auth_header, json=test_chat_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Chat description updated successfully"

@pytest.mark.asyncio
async def test_update_chat_message_pin(client: AsyncClient, get_auth_header: dict):
     """Test pinning a chat message."""
     test_chat_data = {
          "chat_id": 123456,
        "message_id": 789
     }
     response = await client.put(
         "/bots/1/chats/pin_message", headers=get_auth_header, json=test_chat_data
    )
     assert response.status_code == 200
     data = response.json()
     assert data["message"] == "Message pinned successfully"


@pytest.mark.asyncio
async def test_update_chat_message_unpin(client: AsyncClient, get_auth_header: dict):
    """Test unpinning a chat message."""
    test_chat_data = {
        "chat_id": 123456,
        "message_id": 789
    }
    response = await client.put(
        "/bots/1/chats/unpin_message", headers=get_auth_header, json=test_chat_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Message unpinned successfully"

@pytest.mark.asyncio
async def test_update_chat_title_unauthorized(client: AsyncClient):
    """Test update a chat title without authorization."""
    test_chat_data = {
        "chat_id": 123456,
        "title": "Test Chat Title",
    }
    response = await client.put("/bots/1/chats/title", json=test_chat_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_chat_description_unauthorized(client: AsyncClient):
    """Test update a chat description without authorization."""
    test_chat_data = {
        "chat_id": 123456,
        "description": "Test Description",
    }
    response = await client.put("/bots/1/chats/description", json=test_chat_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_chat_message_pin_unauthorized(client: AsyncClient):
    """Test update pin message without authorization."""
    test_chat_data = {
        "chat_id": 123456,
        "message_id": 789
    }
    response = await client.put("/bots/1/chats/pin_message", json=test_chat_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_chat_message_unpin_unauthorized(client: AsyncClient):
    """Test update unpin message without authorization."""
    test_chat_data = {
        "chat_id": 123456,
        "message_id": 789
    }
    response = await client.put("/bots/1/chats/unpin_message", json=test_chat_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_chat_title_invalid_chat_id(client: AsyncClient, get_auth_header: dict):
    """Test update a chat title with invalid chat id"""
    test_chat_data = {
        "chat_id": "invalid",
        "title": "Test Chat Title",
    }
    response = await client.put(
        "/bots/1/chats/title", headers=get_auth_header, json=test_chat_data
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_chat_description_invalid_chat_id(client: AsyncClient, get_auth_header: dict):
    """Test update a chat description with invalid chat id"""
    test_chat_data = {
       "chat_id": "invalid",
        "description": "Test Description",
    }
    response = await client.put(
         "/bots/1/chats/description", headers=get_auth_header, json=test_chat_data
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_chat_message_pin_invalid_chat_id(client: AsyncClient, get_auth_header: dict):
    """Test pin message with invalid chat id"""
    test_chat_data = {
        "chat_id": "invalid",
        "message_id": 789
    }
    response = await client.put(
        "/bots/1/chats/pin_message", headers=get_auth_header, json=test_chat_data
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_chat_message_unpin_invalid_chat_id(client: AsyncClient, get_auth_header: dict):
    """Test unpin message with invalid chat id"""
    test_chat_data = {
        "chat_id": "invalid",
        "message_id": 789
    }
    response = await client.put(
        "/bots/1/chats/unpin_message", headers=get_auth_header, json=test_chat_data
    )
    assert response.status_code == 400