import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from datetime import datetime

from src.api.controllers import LogController
from src.api.schemas import LogCreate, LogUpdate
from src.core.log_manager import LogManager

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_log_manager() -> AsyncMock:
    """
    Fixture to create a mock LogManager.
    """
    return AsyncMock(spec=LogManager)

@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock()
    mock.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    return mock

@pytest.mark.asyncio
async def test_create_log_success(mock_log_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the create_log method successfully creates a log entry.
    """
    controller = LogController(log_manager=mock_log_manager)
    log_data = LogCreate(level="INFO", service="test_service", message="Test message", timestamp="2024-01-01T12:00:00Z")
    mock_log_manager.create_log.return_value = None

    result = await controller.create_log(log_data=log_data, user={"id": 1})

    assert result.message == "Log entry created successfully"
    mock_log_manager.create_log.assert_called_once()

@pytest.mark.asyncio
async def test_get_logs_success(mock_log_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_logs method successfully retrieves log entries based on filters.
    """
    controller = LogController(log_manager=mock_log_manager)
    mock_log_manager.get_logs.return_value = [
          AsyncMock(id=1, level="INFO", service="test_service", message="Test message", timestamp=datetime.utcnow())
    ]

    result = await controller.get_logs(level="INFO", service="test_service", user={"id": 1})

    assert len(result.items) == 1
    mock_log_manager.get_logs.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_logs_success(mock_log_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_all_logs method successfully retrieves all log entries.
    """
    controller = LogController(log_manager=mock_log_manager)
    mock_log_manager.get_all_logs.return_value = [
         AsyncMock(id=1, level="INFO", service="test_service", message="Test message", timestamp=datetime.utcnow()),
         AsyncMock(id=2, level="ERROR", service="test_service", message="Test message", timestamp=datetime.utcnow()),
    ]
    result = await controller.get_all_logs(user={"id": 1})
    assert len(result.items) == 2
    mock_log_manager.get_all_logs.assert_called_once()


@pytest.mark.asyncio
async def test_create_log_error(mock_log_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the create_log method raises an exception when creation fails.
    """
    controller = LogController(log_manager=mock_log_manager)
    log_data = LogCreate(level="INFO", service="test_service", message="Test message", timestamp="2024-01-01T12:00:00Z")
    mock_log_manager.create_log.side_effect = Exception("Test Exception")

    with pytest.raises(HTTPException) as excinfo:
         await controller.create_log(log_data=log_data, user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR