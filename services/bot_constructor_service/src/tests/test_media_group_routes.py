import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.config import settings


@pytest.mark.asyncio
async def test_create_media_group(client: AsyncClient, get_auth_header: dict):
    """Test creating a new media group block."""
    test_media_group_data = {
        "items": [{"type": "photo", "media": "test_url", "caption": "test_caption"}]
    }
    response = await client.post(
        "/bots/1/media_groups/", headers=get_auth_header, json=test_media_group_data
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["items"] == test_media_group_data["items"]
    assert data["type"] == "media_group"


@pytest.mark.asyncio
async def test_get_media_group_by_id(client: AsyncClient, get_auth_header: dict):
    """Test getting a media group block by ID."""
    test_media_group_data = {
       "items": [{"type": "photo", "media": "test_url", "caption": "test_caption"}]
    }
    create_response = await client.post(
       "/bots/1/media_groups/", headers=get_auth_header, json=test_media_group_data
    )
    assert create_response.status_code == 201
    created_media_group = create_response.json()
    media_group_id = created_media_group["id"]
    response = await client.get(
        f"/bots/1/media_groups/{media_group_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == media_group_id
    assert data["items"] == test_media_group_data["items"]
    assert data["type"] == "media_group"

@pytest.mark.asyncio
async def test_get_all_media_groups(client: AsyncClient, get_auth_header: dict):
    """Test getting all media groups."""
    test_media_group_data1 = {
        "items": [{"type": "photo", "media": "test_url_1", "caption": "test_caption_1"}]
    }
    test_media_group_data2 = {
       "items": [{"type": "video", "media": "test_url_2", "caption": "test_caption_2"}]
    }
    await client.post("/bots/1/media_groups/", headers=get_auth_header, json=test_media_group_data1)
    await client.post("/bots/1/media_groups/", headers=get_auth_header, json=test_media_group_data2)

    response = await client.get("/bots/1/media_groups/", headers=get_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 2

    items = [item["items"] for item in data["items"]]
    assert test_media_group_data1["items"] in items
    assert test_media_group_data2["items"] in items

@pytest.mark.asyncio
async def test_update_media_group(client: AsyncClient, get_auth_header: dict):
    """Test updating a media group block."""
    test_media_group_data = {
        "items": [{"type": "photo", "media": "test_url", "caption": "test_caption"}]
    }
    create_response = await client.post(
        "/bots/1/media_groups/", headers=get_auth_header, json=test_media_group_data
    )
    assert create_response.status_code == 201
    created_media_group = create_response.json()
    media_group_id = created_media_group["id"]
    update_data = {"items": [{"type": "video", "media": "updated_test_url", "caption": "updated_caption"}]}
    response = await client.put(
        f"/bots/1/media_groups/{media_group_id}", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == media_group_id
    assert data["items"] == update_data["items"]
    assert data["type"] == "media_group"

@pytest.mark.asyncio
async def test_delete_media_group(client: AsyncClient, get_auth_header: dict):
    """Test deleting a media group block."""
    test_media_group_data = {
         "items": [{"type": "photo", "media": "test_url", "caption": "test_caption"}]
    }
    create_response = await client.post(
        "/bots/1/media_groups/", headers=get_auth_header, json=test_media_group_data
    )
    assert create_response.status_code == 201
    created_media_group = create_response.json()
    media_group_id = created_media_group["id"]
    response = await client.delete(
        f"/bots/1/media_groups/{media_group_id}", headers=get_auth_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Media group block deleted successfully"


    response_get = await client.get(
        f"/bots/1/media_groups/{media_group_id}", headers=get_auth_header
    )
    assert response_get.status_code == 404

@pytest.mark.asyncio
async def test_create_media_group_unauthorized(client: AsyncClient):
    """Test creating a media group without authorization."""
    test_media_group_data = {
        "items": [{"type": "photo", "media": "test_url", "caption": "test_caption"}]
    }
    response = await client.post("/bots/1/media_groups/", json=test_media_group_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_media_group_by_id_unauthorized(client: AsyncClient):
    """Test getting a media group by id without authorization."""
    response = await client.get("/bots/1/media_groups/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_media_group_unauthorized(client: AsyncClient):
    """Test update a media group without authorization."""
    update_data = {"items": [{"type": "video", "media": "updated_test_url", "caption": "updated_caption"}]}
    response = await client.put("/bots/1/media_groups/1", json=update_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_media_group_unauthorized(client: AsyncClient):
    """Test delete a media group without authorization."""
    response = await client.delete("/bots/1/media_groups/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_media_group_not_found(client: AsyncClient, get_auth_header: dict):
    """Test getting a media group that does not exist."""
    response = await client.get(
        "/bots/1/media_groups/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_media_group_not_found(client: AsyncClient, get_auth_header: dict):
    """Test updating a media group that does not exist."""
    update_data = {"items": [{"type": "video", "media": "updated_test_url", "caption": "updated_caption"}]}
    response = await client.put(
        "/bots/1/media_groups/999", headers=get_auth_header, json=update_data
    )
    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_delete_media_group_not_found(client: AsyncClient, get_auth_header: dict):
    """Test deleting a media group that does not exist."""
    response = await client.delete(
         "/bots/1/media_groups/999", headers=get_auth_header
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_media_group_invalid_bot_id(client: AsyncClient, get_auth_header: dict):
    """Test creating a media group with invalid bot id."""
    test_media_group_data = {
        "items": [{"type": "photo", "media": "test_url", "caption": "test_caption"}],
        "bot_id": "invalid_id"
    }
    response = await client.post(
        "/bots/1/media_groups/", headers=get_auth_header, json=test_media_group_data
    )
    assert response.status_code == 400