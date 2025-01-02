import os
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from .models.base import Base

async_engine = create_async_engine(settings.DATABASE_URL, echo=settings.DB_ECHO, future=True)

AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

metadata = MetaData()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator for obtaining database sessions.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Initializes the database and creates necessary tables (if they don't exist).
    """
    try:
        async with async_engine.begin() as conn:
            logger.info("Initializing database...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error during database initialization: {e}")
        raise


async def close_engine():
    """
    Disposes of the database engine and closes connections.
    """
    try:
        logger.info("Closing database connection...")
        await async_engine.dispose()
        logger.info("Database connection closed")
    except SQLAlchemyError as e:
        logger.error(f"Error during closing the database connection: {e}")
        raise


async def check_db_connection(session: AsyncSession) -> bool:
    """
    Checks the connection to the database by running a simple query.
    """
    try:
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except SQLAlchemyError as e:
        logger.error(f"Database connection check failed: {e}")
        return False