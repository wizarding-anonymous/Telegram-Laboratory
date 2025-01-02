import asyncio
import os
import re
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import command
from alembic.config import Config as AlembicConfig
from loguru import logger
from src.config import settings
from src.core.utils.exceptions import DatabaseException
from src.db.repositories.schema_repository import SchemaRepository
from src.db.database import Base


class DatabaseManager:
    """
    Manages database connections, DSN generation, and migrations for both meta and individual bot databases.
    """

    def __init__(self):
        self.meta_engine: AsyncEngine = self._create_meta_engine()
        self.alembic_config: AlembicConfig = self._setup_alembic_config()

    def _create_meta_engine(self) -> AsyncEngine:
        """Creates a database engine for the meta database."""
        try:
            meta_db_url = settings.DATABASE_URL
            logger.info(f"Creating meta database engine with url: {meta_db_url}")
            engine = create_async_engine(meta_db_url, echo=settings.DB_ECHO)
            return engine
        except Exception as e:
            logger.error(f"Error creating meta database engine: {e}")
            raise DatabaseException(f"Failed to create meta database engine: {e}") from e

    def _setup_alembic_config(self) -> AlembicConfig:
        """Configures Alembic for database migrations."""
        try:
            alembic_config = AlembicConfig(settings.ALEMBIC_CONFIG_PATH)
            alembic_config.set_main_option(
                "sqlalchemy.url", str(self.meta_engine.url).replace("%", "%%")
            )
            logger.info(f"Alembic configured with url: {alembic_config.get_main_option('sqlalchemy.url')}")
            return alembic_config
        except Exception as e:
            logger.error(f"Error configuring Alembic: {e}")
            raise DatabaseException(f"Failed to configure Alembic: {e}") from e


    async def check_db_connection(self) -> bool:
        """Checks the connection to the meta database."""
        try:
            async with self.meta_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Meta database connection is healthy")
            return True
        except OperationalError as e:
            logger.error(f"Database connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when checking database connection: {e}")
            return False

    def generate_dsn(self, bot_id: int) -> str:
        """Generates a DSN string for a specific bot."""
        try:
           db_name = f"db_bot_{bot_id}"
           dsn = str(settings.DATABASE_URL).replace(
                f"/{os.path.basename(str(settings.DATABASE_URL))}",
                f"/{db_name}"
            )
           logger.info(f"DSN generated for bot {bot_id}: {dsn}")
           return dsn
        except Exception as e:
            logger.error(f"Error generating DSN for bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to generate DSN for bot {bot_id}: {e}") from e


    async def create_bot_database(self, bot_id: int, schema_repository: SchemaRepository) -> str:
        """Creates a database for a specific bot and applies migrations."""
        dsn = self.generate_dsn(bot_id)
        try:
            logger.info(f"Creating database for bot {bot_id} with DSN: {dsn}")
            engine = create_engine(dsn)
            with engine.connect() as connection:
                connection.execute(text(f"CREATE DATABASE {os.path.basename(dsn)}"))
            logger.info(f"Database created successfully for bot {bot_id}")

            await self._apply_migrations(dsn, bot_id)

            await schema_repository.create(bot_id=bot_id, dsn=dsn)

            logger.info(f"Migrations applied successfully for bot {bot_id}")
            return dsn
        except Exception as e:
            logger.error(f"Error creating or applying migrations for bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to create or apply migrations for bot {bot_id}: {e}") from e

    async def delete_bot_database(self, bot_id: int, schema_repository: SchemaRepository) -> None:
            """Deletes a specific bot's database."""
            dsn = self.generate_dsn(bot_id)
            try:
                logger.info(f"Deleting database for bot {bot_id} with DSN: {dsn}")
                engine = create_engine(dsn)
                with engine.connect() as connection:
                   connection.execute(text(f"DROP DATABASE {os.path.basename(dsn)} WITH (FORCE)"))
                logger.info(f"Database deleted successfully for bot {bot_id}")
                await schema_repository.delete_by_bot_id(bot_id=bot_id)
            except Exception as e:
                logger.error(f"Error deleting database for bot {bot_id}: {e}")
                raise DatabaseException(f"Failed to delete database for bot {bot_id}: {e}") from e

    async def _apply_migrations(self, dsn: str, bot_id: int) -> None:
        """Applies Alembic migrations to a specific bot database."""
        try:
            logger.info(f"Applying migrations for bot {bot_id} with DSN: {dsn}")
            alembic_config = AlembicConfig(settings.ALEMBIC_CONFIG_PATH)
            alembic_config.set_main_option("sqlalchemy.url", str(dsn).replace("%", "%%"))
            command.upgrade(alembic_config, "head")
            logger.info(f"Migrations applied successfully for bot {bot_id}")
        except Exception as e:
            logger.error(f"Error applying migrations for bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to apply migrations for bot {bot_id}: {e}") from e


    async def apply_migrations_for_all_bots(self, schema_repository: SchemaRepository) -> None:
       """Applies migrations for all bots."""
       try:
            logger.info("Starting to apply migrations for all bots...")
            all_schemas = await schema_repository.get_all()
            for schema in all_schemas:
              logger.info(f"Applying migrations for bot: {schema.bot_id}")
              await self._apply_migrations(schema.dsn, schema.bot_id)
            logger.info("Migrations applied for all bots successfully")
       except Exception as e:
            logger.error(f"Error applying migrations for all bots: {e}")
            raise DatabaseException(f"Failed to apply migrations for all bots: {e}") from e

    async def close_engine(self) -> None:
        """Closes the database engine."""
        if self.meta_engine:
           logger.info("Closing meta database engine")
           await self.meta_engine.dispose()
           logger.info("Meta database engine closed")

    def get_alembic_config(self, dsn: Optional[str] = None) -> AlembicConfig:
      """Returns Alembic Config object"""
      alembic_config = AlembicConfig(settings.ALEMBIC_CONFIG_PATH)
      if dsn:
        alembic_config.set_main_option("sqlalchemy.url", str(dsn).replace("%", "%%"))
      else:
        alembic_config.set_main_option(
            "sqlalchemy.url", str(self.meta_engine.url).replace("%", "%%")
        )
      return alembic_config