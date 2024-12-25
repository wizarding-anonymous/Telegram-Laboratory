# services/auth_service/src/db/database.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from alembic.config import Config
from alembic import command
from loguru import logger
from src.config import settings
from typing import AsyncGenerator

# Настройка ThreadPoolExecutor для асинхронного выполнения миграций
executor = ThreadPoolExecutor(max_workers=1)

# Создание асинхронного движка SQLAlchemy
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,
    future=True,
)

# Создание фабрики сессий
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создаёт и возвращает асинхронную сессию базы данных для использования в зависимостях FastAPI.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """
    Инициализация базы данных. Проверяет подключение к базе данных и применяет миграции.
    """
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection is OK")
        await apply_migrations_async()
    except Exception as e:
        logger.error(f"DB initialization error: {str(e)}")
        raise

async def close_db():
    """
    Закрывает соединение с базой данных.
    """
    try:
        await async_engine.dispose()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")

def apply_migrations_sync():
    """
    Применяет миграции синхронно с помощью Alembic.
    """
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", settings.ALEMBIC_SCRIPT_LOCATION)
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.ALEMBIC_URL))
    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully")
    except Exception as e:
        logger.error(f"Error applying migrations: {str(e)}")
        raise

async def apply_migrations_async():
    """
    Применяет миграции асинхронно с использованием ThreadPoolExecutor.
    """
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, apply_migrations_sync)
    except Exception as e:
        logger.error(f"Async migration failed: {str(e)}")
        raise

# Дополнительные функции для управления соединением (опционально)
async def create_all_tables():
    """
    Создаёт все таблицы в базе данных. Используется только в разработке.
    """
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

async def drop_all_tables():
    """
    Удаляет все таблицы из базы данных. Используется только в разработке.
    """
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("All tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping tables: {str(e)}")
        raise