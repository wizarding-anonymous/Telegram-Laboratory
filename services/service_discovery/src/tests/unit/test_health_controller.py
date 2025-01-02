import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status

from src.api.controllers import HealthController
from src.db.database import check_db_connection

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
def mock_session():
    """
    Fixture to create a mock async session.
    """
    return AsyncMock()

@pytest.mark.asyncio
async def test_health_check_success(mock_session: AsyncMock, mocker):
    """
    Test that the health check returns a successful response when the database is connected.
    """
    mocker.patch("src.api.controllers.health_controller.check_db_connection", return_value = True)
    controller = HealthController(session=mock_session)
    
    response = await controller.check_health()
    
    assert response.status == "ok"
    assert "healthy" in response.details
    
    
@pytest.mark.asyncio
async def test_health_check_db_error(mock_session: AsyncMock, mocker):
    """
    Test that the health check raises an HTTPException when the database connection fails.
    """
    mocker.patch("src.api.controllers.health_controller.check_db_connection", side_effect = Exception("Database error"))
    controller = HealthController(session=mock_session)
    
    with pytest.raises(HTTPException) as excinfo:
        await controller.check_health()
    
    assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Database connection failed" in excinfo.value.detail
    
    
@pytest.mark.asyncio
async def test_health_check_service_error(mock_session: AsyncMock, mocker):
     """
    Test that the health check raises an HTTPException when an unexpected error occurs.
    """
     mocker.patch("src.api.controllers.health_controller.check_db_connection", side_effect=Exception("Some service error"))
     controller = HealthController(session=mock_session)
    
     with pytest.raises(HTTPException) as excinfo:
        await controller.check_health()
    
     assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
     assert "Service health check failed" in excinfo.value.detail