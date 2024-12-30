import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_webhook(client: AsyncClient, get_auth_header: dict):
    """Test creating a new webhook block."""
    test_webhook_data = {"url": "https://example.com/webhook"}
    response = await client.post(
        "/bots/1/webhooks/", headers=get_auth_header, json=test_webhook_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["url"] == test_webhook_data["url"]
    assert data["type"] == "set_webhook"


@pytest.mark.asyncio
async def test_get_webhook_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a webhook block by ID."""
    test_webhook_data = {"url": "https://example.com/webhook"}
    create_response = await client.post(
        "/bots/1/webhooks/", headers=get_auth_header, json=test_webhook_data
    )
    assert create_response.status_code == 201
    created_webhook = create_response.json()
    webhook_id = created_webhook["id"]
    response = await client.get(
        f"/blocks/{webhook_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == webhook_id
    assert data["url"] == test_webhook_data["url"]
    assert data["type"] == "set_webhook"


@pytest.mark.asyncio
async def test_update_webhook(client: AsyncClient, get_auth_header: dict):
    """Test updating a webhook block."""
    test_webhook_data = {"url": "https://example.com/webhook"}
    create_response = await client.post(
        "/bots/1/webhooks/", headers=get_auth_header, json=test_webhook_data
    )
    assert create_response.status_code == 201
    created_webhook = create_response.json()
    webhook_id = created_webhook["id"]
    update_data = {"url": "https://example.com/updated_webhook"}
    response = await client.put(
        f"/blocks/{webhook_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == webhook_id
    assert data["url"] == update_data["url"]


@pytest.mark.asyncio
async def test_delete_webhook(client: AsyncClient, get_auth_header: dict):
    """Test deleting a webhook block."""
    test_webhook_data = {"url": "https://example.com/webhook"}
    create_response = await client.post(
        "/bots/1/webhooks/", headers=get_auth_header, json=test_webhook_data
    )
    assert create_response.status_code == 201
    created_webhook = create_response.json()
    webhook_id = created_webhook["id"]
    response = await client.delete(
        f"/blocks/{webhook_id}", headers=get_auth_header
    )
    assert response.status_code == 204

    response_get = await client.get(
        f"/blocks/{webhook_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_webhook_unauthorized(client: AsyncClient):
    """Test creating a webhook without authorization."""
    test_webhook_data = {"url": "https://example.com/webhook"}
    response = await client.post("/bots/1/webhooks/", json=test_webhook_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_webhook_by_id_unauthorized(client: AsyncClient):
    """Test getting a webhook by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_webhook_unauthorized(client: AsyncClient):
    """Test update a webhook without authorization."""
    update_data = {"url": "https://example.com/updated_webhook"}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_webhook_unauthorized(client: AsyncClient):
    """Test delete a webhook without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_webhook_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a webhook that does not exist."""
    response = await client.get(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_webhook_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a webhook that does not exist."""
    update_data = {"url": "https://example.com/updated_webhook"}
    response = await client.put(
        "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_webhook_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a webhook that does not exist."""
    response = await client.delete(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_webhook_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a webhook with invalid bot id."""
    test_webhook_data = {"url": "https://example.com/webhook", "bot_id": "invalid"}
    response = await client.post(
        "/bots/1/webhooks/", headers=get_auth_header, json=test_webhook_data
    )
    assert response.status_code == 400