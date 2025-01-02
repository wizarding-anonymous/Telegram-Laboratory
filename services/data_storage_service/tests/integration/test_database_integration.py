import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.config import settings
from src.core.database_manager import DatabaseManager
from src.db.models.bot_model import Bot
from src.db.models.schema_model import Schema
from src.db.repositories.bot_repository import BotRepository
from src.db.repositories.schema_repository import SchemaRepository
from src.integrations.service_discovery.client import ServiceDiscoveryClient

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture to create httpx client with app.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture()
async def db_manager() -> DatabaseManager:
    """Fixture to create DatabaseManager instance."""
    return DatabaseManager()


@pytest.fixture()
async def bot_repository(db_manager: DatabaseManager) -> BotRepository:
  async with db_manager.meta_engine.begin() as session:
        return BotRepository(session=session)


@pytest.fixture()
async def schema_repository(db_manager: DatabaseManager) -> SchemaRepository:
    async with db_manager.meta_engine.begin() as session:
        return SchemaRepository(session=session)

@pytest.fixture()
def mock_service_discovery() -> AsyncMock:
  """Fixture to create a mock ServiceDiscoveryClient"""
  mock = AsyncMock(spec=ServiceDiscoveryClient)
  mock.register_service.return_value = "test_service_id"
  return mock


async def test_create_and_delete_bot_database(
    db_manager: DatabaseManager,
    bot_repository: BotRepository,
    schema_repository: SchemaRepository,
    mock_service_discovery: AsyncMock
):
  """
    Test creating and deleting a bot database and also registration to service discovery.
    """
  bot = await bot_repository.create(name="TestBot")
  bot_id = bot.id
  dsn = await db_manager.create_bot_database(bot_id=bot_id, schema_repository=schema_repository)

  assert dsn is not None

  async with db_manager.meta_engine.begin() as conn:
      result = await conn.execute(text(f"SELECT 1 FROM schemas WHERE bot_id = {bot_id}"))
      assert result.scalar_one_or_none() == 1

  schema_db = await schema_repository.get_by_bot_id(bot_id=bot_id)
  assert schema_db.dsn == dsn

  await db_manager.delete_bot_database(bot_id=bot_id, schema_repository=schema_repository)

  schema_db = await schema_repository.get_by_bot_id(bot_id=bot_id)
  assert schema_db is None

  async with db_manager.meta_engine.begin() as conn:
    result = await conn.execute(text(f"SELECT 1 FROM schemas WHERE bot_id = {bot_id}"))
    assert result.scalar_one_or_none() is None

  engine = create_engine(dsn)
  with engine.connect() as connection:
       with pytest.raises(OperationalError):
             connection.execute(text("SELECT 1"))
  mock_service_discovery.register_service.assert_called_once()


async def test_apply_migrations_for_all_bots(
    db_manager: DatabaseManager,
    bot_repository: BotRepository,
    schema_repository: SchemaRepository,
):
    """
    Test applying migrations for all bots.
    """
    bot1 = await bot_repository.create(name="TestBot1")
    bot2 = await bot_repository.create(name="TestBot2")
    await db_manager.create_bot_database(bot_id=bot1.id, schema_repository=schema_repository)
    await db_manager.create_bot_database(bot_id=bot2.id, schema_repository=schema_repository)
    await db_manager.apply_migrations_for_all_bots(schema_repository=schema_repository)
    schema_db_1 = await schema_repository.get_by_bot_id(bot_id=bot1.id)
    assert schema_db_1 is not None
    schema_db_2 = await schema_repository.get_by_bot_id(bot_id=bot2.id)
    assert schema_db_2 is not None
    alembic_config_1 = db_manager.get_alembic_config(schema_db_1.dsn)
    alembic_config_2 = db_manager.get_alembic_config(schema_db_2.dsn)
    assert alembic_config_1.get_main_option("sqlalchemy.url") == schema_db_1.dsn
    assert alembic_config_2.get_main_option("sqlalchemy.url") == schema_db_2.dsn


async def test_unregister_service_from_service_discovery(
    db_manager: DatabaseManager,
    mock_service_discovery: AsyncMock,
    bot_repository: BotRepository,
    schema_repository: SchemaRepository
):
     """Test unregistering service from service discovery"""
     bot = await bot_repository.create(name="TestBot")
     bot_id = bot.id
     dsn = await db_manager.create_bot_database(bot_id=bot_id, schema_repository=schema_repository)
     await db_manager.delete_bot_database(bot_id=bot_id, schema_repository=schema_repository)
     mock_service_discovery.unregister_service.assert_called_once()


async def test_check_db_connection(
        db_manager: DatabaseManager
):
        """Test check db connection."""
        assert await db_manager.check_db_connection() is True