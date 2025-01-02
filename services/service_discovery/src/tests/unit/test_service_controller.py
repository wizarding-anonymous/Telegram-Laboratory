import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status

from src.api.controllers import ServiceController
from src.api.schemas import ServiceCreate, ServiceUpdate
from src.db.repositories import ServiceRepository

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
def mock_service_repository() -> AsyncMock:
    """
    Fixture to create a mock ServiceRepository.
    """
    return AsyncMock(spec=ServiceRepository)

@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock()
    mock.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    return mock

@pytest.mark.asyncio
async def test_create_service_success(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the create_service method successfully creates a service.
    """
    controller = ServiceController(session=AsyncMock())
    service_data = ServiceCreate(name="Test Service", address="127.0.0.1", port=8080, metadata = {"version": "1.0"})
    mock_service_repository.create.return_value = AsyncMock(
        id=1, name="Test Service", address="127.0.0.1", port=8080, metadata = {"version": "1.0"}
    )

    result = await controller.register_service(service_data=service_data, user={"id": 1})

    assert result.id == 1
    assert result.name == "Test Service"
    assert result.address == "127.0.0.1"
    assert result.port == 8080
    mock_service_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_service_success(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_service method successfully retrieves a service.
    """
    controller = ServiceController(session=AsyncMock())
    mock_service_repository.get.return_value = AsyncMock(
        id=1, name="Test Service", address="127.0.0.1", port=8080, metadata = {"version": "1.0"}
    )

    result = await controller.get_service(service_id=1, user={"id": 1})

    assert result.id == 1
    assert result.name == "Test Service"
    assert result.address == "127.0.0.1"
    assert result.port == 8080
    mock_service_repository.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_service_not_found(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_service method raises an HTTPException if service is not found.
    """
    controller = ServiceController(session=AsyncMock())
    mock_service_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
         await controller.get_service(service_id=1, user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_all_services_success(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_all_services method successfully retrieves all services.
    """
    controller = ServiceController(session=AsyncMock())
    mock_service_repository.get_all.return_value = [
        AsyncMock(id=1, name="Test Service 1", address="127.0.0.1", port=8080, metadata = {"version": "1.0"}),
        AsyncMock(id=2, name="Test Service 2", address="127.0.0.2", port=9090, metadata = {"version": "1.0"}),
    ]

    result = await controller.get_all_services(user={"id": 1})

    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[1].id == 2
    mock_service_repository.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_update_service_success(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the update_service method successfully updates a service.
    """
    controller = ServiceController(session=AsyncMock())
    service_data = ServiceUpdate(name="Updated Service", address="127.0.0.2", port=9090, metadata = {"version": "1.0"})
    mock_service_repository.get.return_value = AsyncMock(
        id=1, name="Test Service", address="127.0.0.1", port=8080, metadata = {"version": "1.0"}
    )
    mock_service_repository.update.return_value = AsyncMock(
        id=1, name="Updated Service", address="127.0.0.2", port=9090, metadata = {"version": "1.0"}
    )

    result = await controller.update_service(service_id=1, service_data=service_data, user={"id": 1})

    assert result.id == 1
    assert result.name == "Updated Service"
    assert result.address == "127.0.0.2"
    assert result.port == 9090
    mock_service_repository.update.assert_called_once()
    mock_service_repository.get.assert_called_once()


@pytest.mark.asyncio
async def test_update_service_not_found(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the update_service method raises an HTTPException if service is not found.
    """
    controller = ServiceController(session=AsyncMock())
    service_data = ServiceUpdate(name="Updated Service", address="127.0.0.2", port=9090, metadata = {"version": "1.0"})
    mock_service_repository.get.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await controller.update_service(service_id=1, service_data=service_data, user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_service_success(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the delete_service method successfully deletes a service.
    """
    controller = ServiceController(session=AsyncMock())
    mock_service_repository.get.return_value = AsyncMock(
        id=1, name="Test Service", address="127.0.0.1", port=8080, metadata = {"version": "1.0"}
    )
    result = await controller.delete_service(service_id=1, user={"id": 1})

    assert result.message == "Service unregistered successfully"
    mock_service_repository.delete.assert_called_once()
    mock_service_repository.get.assert_called_once()


@pytest.mark.asyncio
async def test_delete_service_not_found(mock_service_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the delete_service method raises an HTTPException if service is not found.
    """
    controller = ServiceController(session=AsyncMock())
    mock_service_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.delete_service(service_id=1, user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND