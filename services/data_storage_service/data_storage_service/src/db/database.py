from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from src.config import settings
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """
    Returns an asynchronous session for database interaction.
    """
    async with async_session() as session:
        yield session


@handle_exceptions
async def check_db_connection(session: AsyncSession) -> bool:
    """
    Checks if the database connection is alive.
    """
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        raise DatabaseException(f"Database connection error: {e}") from e


async def close_engine() -> None:
    """
    Closes database engine
    """
    if engine:
        await engine.dispose()