import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_bot_settings(client: AsyncClient, get_auth_header: dict):
    """Test creating bot settings for a bot."""
    test_settings_data = {
        "token": "test_token",
        "library": "telegram_api",
    }
    response = await client.post(
        "/bots/1/settings/", headers=get_auth_header, json=test_settings_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["token"] == test_settings_data["token"]
    assert data["library"] == test_settings_data["library"]


@pytest.mark.asyncio
async def test_get_bot_settings(client: AsyncClient, get_auth_header: dict):
    """Test getting bot settings by bot ID."""
    test_settings_data = {
        "token": "test_token",
        "library": "telegram_api",
    }
    create_response = await client.post(
        "/bots/1/settings/", headers=get_auth_header, json=test_settings_data
    )
    assert create_response.status_code == 201
    created_settings = create_response.json()
    bot_id = created_settings["id"]
    response = await client.get(
        f"/bots/{bot_id}/settings", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bot_id
    assert data["token"] == test_settings_data["token"]
    assert data["library"] == test_settings_data["library"]


@pytest.mark.asyncio
async def test_update_bot_settings(client: AsyncClient, get_auth_header: dict):
    """Test updating bot settings."""
    test_settings_data = {
         "token": "test_token",
        "library": "telegram_api",
    }
    create_response = await client.post(
        "/bots/1/settings/", headers=get_auth_header, json=test_settings_data
    )
    assert create_response.status_code == 201
    created_settings = create_response.json()
    bot_id = created_settings["id"]
    update_data = {"token": "new_token", "library": "aiogram"}
    response = await client.put(
        f"/bots/{bot_id}/settings", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bot_id
    assert data["token"] == update_data["token"]
    assert data["library"] == update_data["library"]


@pytest.mark.asyncio
async def test_delete_bot_settings(client: AsyncClient, get_auth_header: dict):
    """Test deleting bot settings."""
    test_settings_data = {
         "token": "test_token",
        "library": "telegram_api",
    }
    create_response = await client.post(
        "/bots/1/settings/", headers=get_auth_header, json=test_settings_data
    )
    assert create_response.status_code == 201
    created_settings = create_response.json()
    bot_id = created_settings["id"]
    response = await client.delete(
        f"/bots/{bot_id}/settings", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Bot settings deleted successfully"

    response_get = await client.get(
        f"/bots/{bot_id}/settings", headers=get_auth_header
    )
    assert response_get.status_code == 200
    data_get = response_get.json()
    assert data_get["token"] == ""
    assert data_get["library"] == "telegram_api"

@pytest.mark.asyncio
async def test_create_bot_settings_unauthorized(client: AsyncClient):
    """Test creating bot settings without authorization."""
    test_settings_data = {"token": "test_token", "library": "telegram_api"}
    response = await client.post("/bots/1/settings/", json=test_settings_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_bot_settings_unauthorized(client: AsyncClient):
    """Test getting bot settings without authorization."""
    response = await client.get("/bots/1/settings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_bot_settings_unauthorized(client: AsyncClient):
    """Test update bot settings without authorization."""
    update_data = {"token": "new_token", "library": "aiogram"}
    response = await client.put("/bots/1/settings", json=update_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_bot_settings_unauthorized(client: AsyncClient):
    """Test delete bot settings without authorization."""
    response = await client.delete("/bots/1/settings")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_bot_settings_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a bot settings that does not exist."""
    response = await client.get(
        "/bots/999/settings", headers=get_auth_header
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_bot_settings_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating bot settings that does not exist."""
    update_data = {"token": "new_token", "library": "aiogram"}
    response = await client.put(
        "/bots/999/settings", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_bot_settings_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting bot settings that does not exist."""
    response = await client.delete(
        "/bots/999/settings", headers=get_auth_header
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_create_bot_settings_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating bot settings with invalid bot id."""
    test_settings_data = {
        "token": "test_token",
        "library": "telegram_api",
        "bot_id": "invalid_id",
    }
    response = await client.post(
         "/bots/1/settings/", headers=get_auth_header, json=test_settings_data
    )
    assert response.status_code == 400