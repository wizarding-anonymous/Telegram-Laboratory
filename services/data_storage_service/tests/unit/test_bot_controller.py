import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from src.api.controllers import BotController
from src.api.schemas import BotCreate, BotUpdate
from src.db.repositories import BotRepository
from src.integrations.auth_service import AuthService
from src.core.database_manager import DatabaseManager



@pytest.fixture
def mock_bot_repository() -> AsyncMock:
    """
    Fixture to create a mock BotRepository.
    """
    return AsyncMock(spec=BotRepository)


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock(spec=AuthService)
    mock.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    return mock


@pytest.fixture
def mock_database_manager() -> AsyncMock:
     """
     Fixture to create a mock DatabaseManager
     """
     mock = AsyncMock(spec=DatabaseManager)
     mock.create_database_for_bot.return_value = "test_dsn"
     mock.get_bot_dsn.return_value = "test_dsn"
     return mock

@pytest.mark.asyncio
async def test_create_bot_success(
    mock_bot_repository: AsyncMock, 
    mock_auth_service: AsyncMock,
    mock_database_manager: AsyncMock
):
    """
    Test that the create_bot method successfully creates a bot.
    """
    controller = BotController(
        session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    bot_data = BotCreate(name="Test Bot", description="A test bot")
    mock_bot_repository.create.return_value = AsyncMock(id=1, name="Test Bot", description="A test bot", user_id=1)

    result = await controller.create_bot(bot_data=bot_data)

    assert result.id == 1
    assert result.name == "Test Bot"
    assert result.description == "A test bot"
    assert result.dsn == "test_dsn"
    mock_bot_repository.create.assert_called_once()
    mock_database_manager.create_database_for_bot.assert_called_once()


@pytest.mark.asyncio
async def test_get_bot_success(
    mock_bot_repository: AsyncMock, 
     mock_auth_service: AsyncMock,
    mock_database_manager: AsyncMock
):
    """
    Test that the get_bot method successfully retrieves a bot.
    """
    controller = BotController(
         session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    mock_bot_repository.get.return_value = AsyncMock(id=1, name="Test Bot", description="A test bot", user_id=1)

    result = await controller.get_bot(bot_id=1)

    assert result.id == 1
    assert result.name == "Test Bot"
    assert result.description == "A test bot"
    assert result.dsn == "test_dsn"
    mock_bot_repository.get.assert_called_once()
    mock_database_manager.get_bot_dsn.assert_called_once()

@pytest.mark.asyncio
async def test_get_bot_not_found(mock_bot_repository: AsyncMock, mock_auth_service: AsyncMock, mock_database_manager: AsyncMock):
    """
    Test that the get_bot method raises an HTTPException if bot is not found.
    """
    controller = BotController(
         session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    mock_bot_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.get_bot(bot_id=1)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_bots_success(mock_bot_repository: AsyncMock, mock_auth_service: AsyncMock, mock_database_manager: AsyncMock):
    """
    Test that the get_all_bots method successfully retrieves all bots.
    """
    controller = BotController(
         session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    mock_bot_repository.get_all.return_value = [
        AsyncMock(id=1, name="Test Bot 1", description="Test bot 1", user_id=1),
        AsyncMock(id=2, name="Test Bot 2", description="Test bot 2", user_id=1),
    ]

    result = await controller.get_all_bots()

    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[0].dsn == "test_dsn"
    mock_bot_repository.get_all.assert_called_once()
    mock_database_manager.get_bot_dsn.assert_called_once()


@pytest.mark.asyncio
async def test_update_bot_success(mock_bot_repository: AsyncMock, mock_auth_service: AsyncMock, mock_database_manager: AsyncMock):
    """
    Test that the update_bot method successfully updates a bot.
    """
    controller = BotController(
       session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    bot_data = BotUpdate(name="Updated Bot", description="Updated test bot")
    mock_bot_repository.get.return_value = AsyncMock(id=1, name="Test Bot", description="A test bot", user_id=1)
    mock_bot_repository.update.return_value = AsyncMock(id=1, name="Updated Bot", description="Updated test bot", user_id=1)

    result = await controller.update_bot(bot_id=1, bot_data=bot_data)

    assert result.id == 1
    assert result.name == "Updated Bot"
    assert result.description == "Updated test bot"
    assert result.dsn == "test_dsn"
    mock_bot_repository.update.assert_called_once()
    mock_bot_repository.get.assert_called_once()
    mock_database_manager.get_bot_dsn.assert_called_once()

@pytest.mark.asyncio
async def test_update_bot_not_found(mock_bot_repository: AsyncMock, mock_auth_service: AsyncMock, mock_database_manager: AsyncMock):
    """
    Test that the update_bot method raises an HTTPException if bot is not found.
    """
    controller = BotController(
       session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    bot_data = BotUpdate(name="Updated Bot", description="Updated test bot")
    mock_bot_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.update_bot(bot_id=1, bot_data=bot_data)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_bot_success(mock_bot_repository: AsyncMock, mock_auth_service: AsyncMock, mock_database_manager: AsyncMock):
    """
    Test that the delete_bot method successfully deletes a bot.
    """
    controller = BotController(
       session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    mock_bot_repository.get.return_value = AsyncMock(id=1, name="Test Bot", description="A test bot", user_id=1)

    result = await controller.delete_bot(bot_id=1)

    assert result.message == "Bot deleted successfully"
    mock_bot_repository.delete.assert_called_once()
    mock_bot_repository.get.assert_called_once()
    mock_database_manager.delete_database_for_bot.assert_called_once()

@pytest.mark.asyncio
async def test_delete_bot_not_found(mock_bot_repository: AsyncMock, mock_auth_service: AsyncMock, mock_database_manager: AsyncMock):
    """
    Test that the delete_bot method raises an HTTPException if bot is not found.
    """
    controller = BotController(
       session=AsyncMock(), auth_service=mock_auth_service, database_manager = mock_database_manager
    )
    mock_bot_repository.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.delete_bot(bot_id=1)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND