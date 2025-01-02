import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status

from src.api.controllers import MetadataController
from src.api.schemas import MetadataCreate, MetadataUpdate
from src.db.repositories import MetadataRepository


@pytest.fixture
def mock_metadata_repository() -> AsyncMock:
    """
    Fixture to create a mock MetadataRepository.
    """
    return AsyncMock(spec=MetadataRepository)

@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock()
    mock.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    return mock

@pytest.mark.asyncio
async def test_create_metadata_success(mock_metadata_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the create_metadata method successfully creates metadata.
    """
    controller = MetadataController(session=AsyncMock())
    metadata_data = MetadataCreate(bot_id=1, key="test_key", value="test_value")
    mock_metadata_repository.create.return_value = AsyncMock(
        id=1, bot_id=1, key="test_key", value="test_value", created_at="test_time"
    )

    result = await controller.create_metadata(metadata_data, current_user={"id": 1})

    assert result.id == 1
    assert result.bot_id == 1
    assert result.key == "test_key"
    assert result.value == "test_value"
    mock_metadata_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_metadata_success(mock_metadata_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_metadata method successfully retrieves metadata.
    """
    controller = MetadataController(session=AsyncMock())
    mock_metadata_repository.get.return_value = AsyncMock(
        id=1, bot_id=1, key="test_key", value="test_value", created_at="test_time"
    )
    result = await controller.get_metadata(metadata_id=1, current_user={"id": 1})

    assert result.id == 1
    assert result.bot_id == 1
    assert result.key == "test_key"
    assert result.value == "test_value"
    mock_metadata_repository.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_metadata_not_found(mock_metadata_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_metadata method raises an HTTPException if metadata is not found.
    """
    controller = MetadataController(session=AsyncMock())
    mock_metadata_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.get_metadata(metadata_id=1, current_user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_metadata_success(mock_metadata_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the update_metadata method successfully updates metadata.
    """
    controller = MetadataController(session=AsyncMock())
    metadata_data = MetadataUpdate(key="updated_key", value="updated_value")
    mock_metadata_repository.get.return_value = AsyncMock(
        id=1, bot_id=1, key="test_key", value="test_value", created_at="test_time"
    )
    mock_metadata_repository.update.return_value = AsyncMock(
       id=1, bot_id=1, key="updated_key", value="updated_value", created_at="test_time"
    )

    result = await controller.update_metadata(metadata_id=1, metadata_data=metadata_data, current_user={"id": 1})

    assert result.id == 1
    assert result.bot_id == 1
    assert result.key == "updated_key"
    assert result.value == "updated_value"
    mock_metadata_repository.update.assert_called_once()
    mock_metadata_repository.get.assert_called_once()

@pytest.mark.asyncio
async def test_update_metadata_not_found(mock_metadata_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the update_metadata method raises an HTTPException if metadata is not found.
    """
    controller = MetadataController(session=AsyncMock())
    metadata_data = MetadataUpdate(key="updated_key", value="updated_value")
    mock_metadata_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.update_metadata(metadata_id=1, metadata_data=metadata_data, current_user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_metadata_success(mock_metadata_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the delete_metadata method successfully deletes metadata.
    """
    controller = MetadataController(session=AsyncMock())
    mock_metadata_repository.get.return_value = AsyncMock(
        id=1, bot_id=1, key="test_key", value="test_value", created_at="test_time"
    )

    result = await controller.delete_metadata(metadata_id=1, current_user={"id": 1})

    assert result.message == "Metadata deleted successfully"
    mock_metadata_repository.delete.assert_called_once()
    mock_metadata_repository.get.assert_called_once()

@pytest.mark.asyncio
async def test_delete_metadata_not_found(mock_metadata_repository: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the delete_metadata method raises an HTTPException if metadata is not found.
    """
    controller = MetadataController(session=AsyncMock())
    mock_metadata_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.delete_metadata(metadata_id=1, current_user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND