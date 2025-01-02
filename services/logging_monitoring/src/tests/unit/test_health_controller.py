import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status

from src.api.controllers import HealthController
from src.db.database import check_db_connection
from src.integrations.prometheus_client import PrometheusClient
from src.integrations.auth_service.client import AuthService


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_session():
    """
    Fixture to create a mock async session.
    """
    return AsyncMock()

@pytest.fixture
def mock_prometheus_client() -> AsyncMock:
    """
    Fixture to create a mock PrometheusClient.
    """
    mock = AsyncMock(spec=PrometheusClient)
    mock.check_connection.return_value = True
    return mock

@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock(spec=AuthService)
    mock.check_health.return_value = True
    return mock


@pytest.mark.asyncio
async def test_health_check_success(mock_session: AsyncMock, mock_prometheus_client: AsyncMock, mock_auth_service: AsyncMock, mocker):
    """
    Test that the health check returns a successful response when the database is connected.
    """
    mocker.patch("src.api.controllers.health_controller.check_db_connection", return_value = True)
    controller = HealthController(session=mock_session, prometheus_client=mock_prometheus_client, auth_service = mock_auth_service)
    
    response = await controller.check_health()
    
    assert response.status == "ok"
    assert "healthy" in response.details
    
    
@pytest.mark.asyncio
async def test_health_check_db_error(mock_session: AsyncMock, mock_prometheus_client: AsyncMock, mock_auth_service: AsyncMock, mocker):
    """
    Test that the health check raises an HTTPException when the database connection fails.
    """
    mocker.patch("src.api.controllers.health_controller.check_db_connection", return_value=False)
    controller = HealthController(session=mock_session, prometheus_client=mock_prometheus_client, auth_service = mock_auth_service)
    
    with pytest.raises(HTTPException) as excinfo:
        await controller.check_health()
    
    assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Service health check failed" in excinfo.value.detail

@pytest.mark.asyncio
async def test_health_check_prometheus_error(mock_session: AsyncMock, mock_prometheus_client: AsyncMock, mock_auth_service: AsyncMock, mocker):
    """
    Test that the health check raises an HTTPException when the prometheus connection fails.
    """
    mocker.patch("src.api.controllers.health_controller.check_db_connection", return_value=True)
    mock_prometheus_client.check_connection.return_value = False
    controller = HealthController(session=mock_session, prometheus_client=mock_prometheus_client, auth_service = mock_auth_service)
    
    with pytest.raises(HTTPException) as excinfo:
        await controller.check_health()
    
    assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Service health check failed" in excinfo.value.detail

@pytest.mark.asyncio
async def test_health_check_auth_service_error(mock_session: AsyncMock, mock_prometheus_client: AsyncMock, mock_auth_service: AsyncMock, mocker):
    """
    Test that the health check raises an HTTPException when the auth service connection fails.
    """
    mocker.patch("src.api.controllers.health_controller.check_db_connection", return_value=True)
    mock_auth_service.check_health.return_value = False
    controller = HealthController(session=mock_session, prometheus_client=mock_prometheus_client, auth_service = mock_auth_service)
    
    with pytest.raises(HTTPException) as excinfo:
        await controller.check_health()
    
    assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Service health check failed" in excinfo.value.detail


@pytest.mark.asyncio
async def test_health_check_unexpected_error(mock_session: AsyncMock, mock_prometheus_client: AsyncMock, mock_auth_service: AsyncMock, mocker):
    """
    Test that the health check raises an HTTPException when an unexpected error occurs.
    """
    mocker.patch("src.api.controllers.health_controller.check_db_connection", side_effect=Exception("Some service error"))
    controller = HealthController(session=mock_session, prometheus_client=mock_prometheus_client, auth_service = mock_auth_service)
    
    with pytest.raises(HTTPException) as excinfo:
         await controller.check_health()
    
    assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Service health check failed" in excinfo.value.detail