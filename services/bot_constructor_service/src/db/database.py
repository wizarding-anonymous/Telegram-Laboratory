from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from loguru import logger
import os
from typing import AsyncGenerator, Optional
from src.config import settings
from urllib.parse import urlparse, urlunparse

# Load database URL from environment variables
DATABASE_URL = settings.DATABASE_URL

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
        except Exception as e:
            logger.error(f"Error creating database session: {e}")
            raise
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

def get_db_uri(bot_id: int) -> str:
        """
        Generates a database uri for a bot based on the base url from settings
        """
        parsed_url = urlparse(settings.DATABASE_URL)
        
        # Construct the new database name
        new_database_name = f"db_bot_{bot_id}"
        
        # Construct the new database URL
        new_url = urlunparse(parsed_url._replace(path=f"/{new_database_name}"))
        
        logger.debug(f"Generated database URL for bot ID {bot_id}: {new_url}")
        return new_url

async def apply_migrations():
    """Applies database migrations."""
    try:
        from alembic import config, command
        alembic_config = config.Config()
        alembic_config.set_main_option("script_location", "src/db/migrations")
        alembic_config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        logger.info("Applying database migrations...")
        command.upgrade(alembic_config, "head")
        logger.info("Database migrations applied successfully")
    except Exception as e:
         logger.error(f"Error applying database migrations: {e}")
         raise