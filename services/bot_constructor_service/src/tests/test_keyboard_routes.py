import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_keyboard(client: AsyncClient, get_auth_header: dict):
    """Test creating a new keyboard block."""
    test_keyboard_data = {"buttons": [["button1", "button2"]], "type": "reply"}
    response = await client.post(
        "/bots/1/keyboards/", headers=get_auth_header, json=test_keyboard_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["buttons"] == test_keyboard_data["buttons"]
    assert data["type"] == test_keyboard_data["type"]


@pytest.mark.asyncio
async def test_get_keyboard_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a keyboard block by ID."""
    test_keyboard_data = {"buttons": [["button1", "button2"]], "type": "reply"}
    create_response = await client.post(
        "/bots/1/keyboards/", headers=get_auth_header, json=test_keyboard_data
    )
    assert create_response.status_code == 201
    created_keyboard = create_response.json()
    keyboard_id = created_keyboard["id"]
    response = await client.get(
        f"/blocks/{keyboard_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == keyboard_id
    assert data["buttons"] == test_keyboard_data["buttons"]
    assert data["type"] == test_keyboard_data["type"]


@pytest.mark.asyncio
async def test_update_keyboard(client: AsyncClient, get_auth_header: dict):
    """Test updating a keyboard block."""
    test_keyboard_data = {"buttons": [["button1", "button2"]], "type": "reply"}
    create_response = await client.post(
        "/bots/1/keyboards/", headers=get_auth_header, json=test_keyboard_data
    )
    assert create_response.status_code == 201
    created_keyboard = create_response.json()
    keyboard_id = created_keyboard["id"]
    update_data = {"buttons": [["updated1"]], "type": "inline"}
    response = await client.put(
        f"/blocks/{keyboard_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == keyboard_id
    assert data["buttons"] == update_data["buttons"]
    assert data["type"] == update_data["type"]


@pytest.mark.asyncio
async def test_delete_keyboard(client: AsyncClient, get_auth_header: dict):
    """Test deleting a keyboard block."""
    test_keyboard_data = {"buttons": [["button1", "button2"]], "type": "reply"}
    create_response = await client.post(
         "/bots/1/keyboards/", headers=get_auth_header, json=test_keyboard_data
    )
    assert create_response.status_code == 201
    created_keyboard = create_response.json()
    keyboard_id = created_keyboard["id"]
    response = await client.delete(
        f"/blocks/{keyboard_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(
        f"/blocks/{keyboard_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404

@pytest.mark.asyncio
async def test_create_keyboard_unauthorized(client: AsyncClient):
    """Test creating a keyboard without authorization."""
    test_keyboard_data = {"buttons": [["button1", "button2"]], "type": "reply"}
    response = await client.post("/bots/1/keyboards/", json=test_keyboard_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_keyboard_by_id_unauthorized(client: AsyncClient):
    """Test getting a keyboard by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_keyboard_unauthorized(client: AsyncClient):
    """Test update a keyboard without authorization."""
    update_data = {"buttons": [["updated1"]], "type": "inline"}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_keyboard_unauthorized(client: AsyncClient):
    """Test delete a keyboard without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401
    
@pytest.mark.asyncio
async def test_get_keyboard_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a keyboard that does not exist."""
    response = await client.get(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_keyboard_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a keyboard that does not exist."""
    update_data = {"buttons": [["updated1"]], "type": "inline"}
    response = await client.put(
        "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_keyboard_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a keyboard that does not exist."""
    response = await client.delete(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_keyboard_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a keyboard with invalid bot_id"""
    test_keyboard_data = {"buttons": [["button1", "button2"]], "type": "reply", "bot_id": "invalid_id"}
    response = await client.post(
         "/bots/1/keyboards/", headers=get_auth_header, json=test_keyboard_data
    )
    assert response.status_code == 400