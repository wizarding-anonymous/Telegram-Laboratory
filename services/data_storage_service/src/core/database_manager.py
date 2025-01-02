import uuid
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends
from loguru import logger

from src.db.database import get_session
from src.db.models import Schema
from src.db.repositories import SchemaRepository
from src.core.utils import handle_exceptions, generate_random_string
from src.config import settings
from src.core.utils.exceptions import DatabaseException


class DatabaseManager:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.schema_repository = SchemaRepository(session)

    @handle_exceptions
    async def create_database_for_bot(self, bot_id: int, user_id: int) -> str:
        """
        Creates a new database for a bot and returns the DSN.
        If the schema already exists, it will return the DSN.
        """
        logger.info(f"Creating database for bot ID: {bot_id}, user_id: {user_id}")
        existing_schema = await self.schema_repository.get_by_bot_id(bot_id)
        if existing_schema:
            logger.info(f"Schema for bot ID {bot_id} already exists. DSN: {existing_schema.dsn}")
            return existing_schema.dsn  # DSN уже существует

        db_name = f"db_bot_{bot_id}"
        dsn = str(
            settings.DATABASE_URL.replace("data_storage_service_db", db_name)
        )
        logger.debug(f"Generated DSN for bot {bot_id}: {dsn}")
        try:
            engine = create_async_engine(dsn)
            async with engine.begin() as conn:
                await conn.execute(text(f"CREATE DATABASE {db_name};"))
            await engine.dispose()
            logger.info(f"Database '{db_name}' created successfully.")
            # Сохраняем DSN в таблице схем
            await self._save_dsn(bot_id=bot_id, dsn=dsn)
            logger.info(f"DSN for bot {bot_id} saved to database.")
            return dsn
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database for bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to create database: {e}") from e

    @handle_exceptions
    async def delete_database_for_bot(self, bot_id: int) -> None:
        """
        Deletes the database for a bot.
        """
        logger.info(f"Deleting database for bot ID: {bot_id}")
        schema = await self.schema_repository.get_by_bot_id(bot_id)
        if not schema:
            logger.warning(f"Schema with bot_id '{bot_id}' not found.")
            raise DatabaseException(f"Schema with bot_id '{bot_id}' not found.")

        dsn = schema.dsn
        db_name = dsn.split("/")[-1]
        logger.debug(f"DSN for deletion: {dsn}, database name: {db_name}")

        try:
            engine = create_async_engine(settings.DATABASE_URL)
            async with engine.begin() as conn:
                await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name};"))
            await engine.dispose()
            logger.info(f"Database '{db_name}' deleted successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete database for bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to delete database: {e}") from e

    @handle_exceptions
    async def get_bot_dsn(self, bot_id: int) -> str:
        """
         Retrieves the DSN for a bot by bot_id.
        """
        logger.info(f"Getting DSN for bot ID: {bot_id}")
        schema = await self.schema_repository.get_by_bot_id(bot_id)
        if not schema:
            logger.warning(f"Schema with bot_id '{bot_id}' not found.")
            raise DatabaseException(f"Schema with bot_id '{bot_id}' not found.")
        logger.debug(f"DSN for bot {bot_id}: {schema.dsn}")
        return schema.dsn

    @handle_exceptions
    async def _save_dsn(self, bot_id: int, dsn: str) -> None:
        """
        Saves generated DSN to the database.
        """
        logger.info(f"Saving DSN for bot ID: {bot_id}")
        try:
            schema_data = Schema(bot_id=bot_id, dsn=dsn)
            await self.schema_repository.create(schema_data)
            logger.info(f"DSN for bot {bot_id} saved successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Failed to save DSN to db for bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to save DSN to db: {e}") from e