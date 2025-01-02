import pytest
from httpx import AsyncClient
from typing import Dict, Any
from src.app import app
from src.config import settings


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def get_auth_header() -> Dict[str, str]:
    """
    Fixture to get authorization header.
    """
    return {"Authorization": f"Bearer test_token"}


@pytest.fixture(scope="session")
async def client():
    """
    Fixture to create httpx client with app.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client