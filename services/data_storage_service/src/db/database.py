# services\data_storage_service\src\db\database.py
import os
from typing import AsyncGenerator, Optional

from alembic.config import Config
from alembic import command
from loguru import logger
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from concurrent.futures import ThreadPoolExecutor
import asyncio

from .models.base import Base

ASYNC_DATABASE_URL = (
    "postgresql+asyncpg://bot_user:bot_password@localhost:5432/data_storage_service"
)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

SYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("+asyncpg", "")
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)

executor = ThreadPoolExecutor(max_workers=1)
metadata = MetaData()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    try:
        async with async_engine.begin() as conn:
            logger.info("Initializing database...")
            logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error during database initialization: {e}")
        raise


async def close_engine():
    try:
        logger.info("Closing database connection...")
        await async_engine.dispose()
        logger.info("Database connection closed")
    except SQLAlchemyError as e:
        logger.error(f"Error during closing the database connection: {e}")
        raise


async def check_db_connection(session: AsyncSession) -> bool:
    try:
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except SQLAlchemyError as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def create_bot_database(bot_id: int) -> str:
    try:
        database_name = f"bot_{bot_id}"
        async with async_engine.begin() as conn:
            await conn.execute(text(f"CREATE DATABASE {database_name}"))
        dsn = f"postgresql+asyncpg://bot_user:bot_password@localhost:5432/{database_name}"
        logger.info(f"Created database for bot {bot_id}")
        return dsn
    except SQLAlchemyError as e:
        logger.error(f"Error creating database for bot {bot_id}: {e}")
        raise


async def check_migrations_status(session: AsyncSession) -> str:
    try:
        result = await session.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        if version:
            if version == "your_expected_version":
                return "healthy"
            else:
                return "pending"
        else:
            return "pending"
    except Exception as e:
        logger.error(f"Error checking migrations: {e}")
        return "unhealthy"


def apply_migrations_sync(bot_id: Optional[int] = None):
    try:
        alembic_cfg = Config("alembic.ini")  
        alembic_cfg.set_main_option("script_location", "src/db/migrations") 
        if bot_id is not None:
            database_name = f"bot_{bot_id}"
            dsn = f"postgresql://bot_user:bot_password@localhost:5432/{database_name}"
            alembic_cfg.set_main_option("sqlalchemy.url", dsn)
        else:
            alembic_cfg.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)

        command.upgrade(alembic_cfg, "head")
        logger.info(
            f"Migrations applied successfully{' for bot ' + str(bot_id) if bot_id else ''}"
        )
    except Exception as e:
        logger.error(
            f"Error applying migrations{' for bot ' + str(bot_id) if bot_id else ''}: {e}"
        )
        raise


async def apply_migrations_async(bot_id: Optional[int] = None):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, apply_migrations_sync, bot_id)


async def apply_migrations(bot_id: Optional[int] = None):
    await apply_migrations_async(bot_id)
