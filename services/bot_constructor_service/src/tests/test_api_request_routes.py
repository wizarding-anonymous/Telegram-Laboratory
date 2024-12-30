import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_api_request(client: AsyncClient, get_auth_header: dict):
    """Test creating a new API request block."""
    test_api_request_data = {
        "url": "https://example.com/api",
        "method": "GET",
    }
    response = await client.post(
        "/bots/1/api_requests/", headers=get_auth_header, json=test_api_request_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["url"] == test_api_request_data["url"]
    assert data["method"] == test_api_request_data["method"]
    assert data["type"] == "make_request"


@pytest.mark.asyncio
async def test_get_api_request_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a API request block by ID."""
    test_api_request_data = {
        "url": "https://example.com/api",
        "method": "GET",
    }
    create_response = await client.post(
       "/bots/1/api_requests/", headers=get_auth_header, json=test_api_request_data
    )
    assert create_response.status_code == 201
    created_api_request = create_response.json()
    api_request_id = created_api_request["id"]
    response = await client.get(
        f"/blocks/{api_request_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == api_request_id
    assert data["url"] == test_api_request_data["url"]
    assert data["method"] == test_api_request_data["method"]
    assert data["type"] == "make_request"


@pytest.mark.asyncio
async def test_update_api_request(client: AsyncClient, get_auth_header: dict):
    """Test updating a API request block."""
    test_api_request_data = {
        "url": "https://example.com/api",
        "method": "GET",
    }
    create_response = await client.post(
       "/bots/1/api_requests/", headers=get_auth_header, json=test_api_request_data
    )
    assert create_response.status_code == 201
    created_api_request = create_response.json()
    api_request_id = created_api_request["id"]
    update_data = {"url": "https://example.com/updated_api", "method": "POST"}
    response = await client.put(
        f"/blocks/{api_request_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == api_request_id
    assert data["url"] == update_data["url"]
    assert data["method"] == update_data["method"]
    assert data["type"] == "make_request"


@pytest.mark.asyncio
async def test_delete_api_request(client: AsyncClient, get_auth_header: dict):
    """Test deleting a API request block."""
    test_api_request_data = {
        "url": "https://example.com/api",
        "method": "GET",
    }
    create_response = await client.post(
        "/bots/1/api_requests/", headers=get_auth_header, json=test_api_request_data
    )
    assert create_response.status_code == 201
    created_api_request = create_response.json()
    api_request_id = created_api_request["id"]
    response = await client.delete(
        f"/blocks/{api_request_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response_get = await client.get(
        f"/blocks/{api_request_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_api_request_unauthorized(client: AsyncClient):
    """Test creating a API request without authorization."""
    test_api_request_data = {
         "url": "https://example.com/api",
        "method": "GET",
    }
    response = await client.post("/bots/1/api_requests/", json=test_api_request_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_api_request_by_id_unauthorized(client: AsyncClient):
    """Test getting a api request by id without authorization."""
    response = await client.get("/blocks/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_api_request_unauthorized(client: AsyncClient):
    """Test update a api request without authorization."""
    update_data = {"url": "https://example.com/updated_api", "method": "POST"}
    response = await client.put("/blocks/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_api_request_unauthorized(client: AsyncClient):
    """Test delete a api request without authorization."""
    response = await client.delete("/blocks/1")
    assert response.status_code == 401
    

@pytest.mark.asyncio
async def test_get_api_request_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a api request that does not exist."""
    response = await client.get(
        "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_update_api_request_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a api request that does not exist."""
    update_data = {"url": "https://example.com/updated_api", "method": "POST"}
    response = await client.put(
         "/blocks/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_api_request_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a api request that does not exist."""
    response = await client.delete(
         "/blocks/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_api_request_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a api_request with invalid bot id."""
    test_api_request_data = {
        "url": "https://example.com/api",
        "method": "GET",
        "bot_id": "invalid_id"
    }
    response = await client.post(
        "/bots/1/api_requests/", headers=get_auth_header, json=test_api_request_data
    )
    assert response.status_code == 400