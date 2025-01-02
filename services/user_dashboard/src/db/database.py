from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from loguru import logger

from src.config import settings
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """
    Returns an asynchronous session for database interaction.
    """
    logger.debug("Creating new database session")
    try:
       async with async_session() as session:
          logger.debug("Database session created")
          yield session
    except Exception as e:
      logger.error(f"Error creating database session: {e}")
      raise
    finally:
        logger.debug("Database session closed")


@handle_exceptions
async def check_db_connection(session: AsyncSession) -> bool:
    """
    Checks if the database connection is alive.
    """
    logger.debug("Checking database connection")
    try:
        await session.execute(text("SELECT 1"))
        logger.debug("Database connection is alive")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseException(f"Database connection error: {e}") from e


async def close_engine() -> None:
    """
    Closes database engine
    """
    logger.debug("Disposing database engine")
    if engine:
        await engine.dispose()
        logger.info("Database engine disposed")