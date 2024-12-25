# services\bot_constructor_service\src\db\database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from loguru import logger
import os
from typing import AsyncGenerator, Optional


# Load database URL from environment variables
DATABASE_URL = "postgresql+asyncpg://bot_user:bot_password@localhost:5432/bot_constructor"

# Create SQLAlchemy Base
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for detailed SQL logs during development
    poolclass=NullPool,  # Avoid connection pooling for simplicity
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Function to get a session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session for FastAPI routes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        async with engine.begin() as connection:
            logger.info("Creating database tables...")
            await connection.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def close_engine():
    """
    Close the database engine during application shutdown.
    """
    try:
        logger.info("Closing database engine...")
        await engine.dispose()
        logger.info("Database engine closed")
    except SQLAlchemyError as e:
        logger.error(f"Error closing database engine: {e}")
        raise

async def check_db_connection(session: AsyncSession) -> Optional[bool]:
    """
    Проверяет подключение к базе данных, выполняя простое запрос.
    Возвращает True, если соединение успешно, False или None в случае ошибки.
    """
    try:
        result = await session.execute("SELECT 1")
        return result.scalar() == 1
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        return None
