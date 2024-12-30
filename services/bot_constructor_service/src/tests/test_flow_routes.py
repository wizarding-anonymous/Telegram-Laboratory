import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings

@pytest.mark.asyncio
async def test_create_flow(client: AsyncClient, get_auth_header: dict):
    """Test creating a new flow chart block."""
    test_flow_data = {
        "logic": {"key": "value"}
    }
    response = await client.post(
        "/bots/1/flow/", headers=get_auth_header, json=test_flow_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["logic"] == test_flow_data["logic"]
    assert data["type"] == "flow_chart"


@pytest.mark.asyncio
async def test_get_flow_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a flow chart block by ID."""
    test_flow_data = {
       "logic": {"key": "value"}
    }
    create_response = await client.post(
       "/bots/1/flow/", headers=get_auth_header, json=test_flow_data
    )
    assert create_response.status_code == 201
    created_flow = create_response.json()
    flow_id = created_flow["id"]
    response = await client.get(
        f"/bots/1/flow/{flow_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == flow_id
    assert data["logic"] == test_flow_data["logic"]
    assert data["type"] == "flow_chart"


@pytest.mark.asyncio
async def test_update_flow(client: AsyncClient, get_auth_header: dict):
    """Test updating a flow chart block."""
    test_flow_data = {
         "logic": {"key": "value"}
    }
    create_response = await client.post(
        "/bots/1/flow/", headers=get_auth_header, json=test_flow_data
    )
    assert create_response.status_code == 201
    created_flow = create_response.json()
    flow_id = created_flow["id"]
    update_data = {"logic": {"key": "updated_value"}}
    response = await client.put(
        f"/bots/1/flow/{flow_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == flow_id
    assert data["logic"] == update_data["logic"]
    assert data["type"] == "flow_chart"

@pytest.mark.asyncio
async def test_delete_flow(client: AsyncClient, get_auth_header: dict):
    """Test deleting a flow chart block."""
    test_flow_data = {
         "logic": {"key": "value"}
    }
    create_response = await client.post(
        "/bots/1/flow/", headers=get_auth_header, json=test_flow_data
    )
    assert create_response.status_code == 201
    created_flow = create_response.json()
    flow_id = created_flow["id"]
    response = await client.delete(
        f"/bots/1/flow/{flow_id}", headers=get_auth_header
    )
    assert response.status_code == 204
    
    response_get = await client.get(
        f"/bots/1/flow/{flow_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_create_flow_unauthorized(client: AsyncClient):
    """Test creating a flow without authorization."""
    test_flow_data = {
         "logic": {"key": "value"}
    }
    response = await client.post("/bots/1/flow/", json=test_flow_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_flow_by_id_unauthorized(client: AsyncClient):
    """Test getting a flow by id without authorization."""
    response = await client.get("/bots/1/flow/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_flow_unauthorized(client: AsyncClient):
    """Test update a flow without authorization."""
    update_data = {"logic": {"key": "updated_value"}}
    response = await client.put("/bots/1/flow/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_flow_unauthorized(client: AsyncClient):
    """Test delete a flow without authorization."""
    response = await client.delete("/bots/1/flow/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_flow_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a flow that does not exist."""
    response = await client.get(
        "/bots/1/flow/999", headers=get_auth_header
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_flow_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a flow that does not exist."""
    update_data = {"logic": {"key": "updated_value"}}
    response = await client.put(
        "/bots/1/flow/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete_flow_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a flow that does not exist."""
    response = await client.delete(
        "/bots/1/flow/999", headers=get_auth_header
    )
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_create_flow_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a flow with invalid bot id."""
    test_flow_data = {
        "logic": {"key": "value"},
        "bot_id": "invalid_id",
    }
    response = await client.post(
        "/bots/1/flow/", headers=get_auth_header, json=test_flow_data
    )
    assert response.status_code == 400