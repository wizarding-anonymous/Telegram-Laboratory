import pytest
from httpx import AsyncClient
from typing import Dict, Any
from unittest.mock import patch
from src.config import settings


@pytest.mark.asyncio
async def test_health_ok(client: AsyncClient, get_auth_header: dict):
    """Test successful health check."""
    with patch("src.db.database.check_db_connection", return_value=True), \
            patch("src.integrations.redis_client.redis_client.exists", return_value=True):
        response = await client.get("/health", headers=get_auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "details" in data
    assert data["version"] == settings.API_VERSION


@pytest.mark.asyncio
async def test_health_database_error(client: AsyncClient, get_auth_header: dict):
    """Test health check with database error."""
    with patch("src.db.database.check_db_connection", return_value=False), \
            patch("src.integrations.redis_client.redis_client.exists", return_value=True):
          response = await client.get("/health", headers=get_auth_header)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_health_redis_error(client: AsyncClient, get_auth_header: dict):
    """Test health check with redis error."""
    with patch("src.db.database.check_db_connection", return_value=True), \
            patch("src.integrations.redis_client.redis_client.exists", return_value=False):
       response = await client.get("/health", headers=get_auth_header)
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_health_unauthorized(client: AsyncClient):
    """Test unauthorized access to health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 401