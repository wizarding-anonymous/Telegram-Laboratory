# services/data_storage_service/src/core/database_manager.py
import uuid
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

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
        If the schema already exists, it will return the DSN
        """
        
        existing_schema = await self.schema_repository.get_by_bot_id(bot_id)
        if existing_schema:
            return existing_schema.dsn # DSN уже существует
    
        db_name = f"db_bot_{bot_id}"
        dsn = str(
            settings.DATABASE_URL.replace("data_storage_service_db", db_name)
        )

        try:
            engine = create_async_engine(dsn)
            async with engine.begin() as conn:
                await conn.execute(text(f"CREATE DATABASE {db_name};"))
            await engine.dispose()
            
            # Сохраняем DSN в таблице схем
            await self._save_dsn(bot_id=bot_id, dsn=dsn)

            return dsn
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to create database: {e}") from e

    @handle_exceptions
    async def delete_database_for_bot(self, bot_id: int) -> None:
        """
        Deletes the database for a bot.
        """
        
        schema = await self.schema_repository.get_by_bot_id(bot_id)
        if not schema:
            raise DatabaseException(f"Schema with bot_id '{bot_id}' not found.")
            
        dsn = schema.dsn
        
        db_name = dsn.split("/")[-1]

        try:
            engine = create_async_engine(settings.DATABASE_URL)
            async with engine.begin() as conn:
                await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name};"))
            await engine.dispose()
            
        except SQLAlchemyError as e:
           raise DatabaseException(f"Failed to delete database: {e}") from e

    
    @handle_exceptions
    async def get_bot_dsn(self, bot_id: int) -> str:
        """
         Retrieves the DSN for a bot by bot_id.
        """
        schema = await self.schema_repository.get_by_bot_id(bot_id)
        if not schema:
             raise DatabaseException(f"Schema with bot_id '{bot_id}' not found.")
        return schema.dsn
    
    @handle_exceptions
    async def _save_dsn(self, bot_id: int, dsn: str) -> None:
         """
        Saves generated DSN to the database
         """
         try:
             schema_data = Schema(bot_id=bot_id, dsn=dsn)
             await self.schema_repository.create(schema_data)
         except SQLAlchemyError as e:
              raise DatabaseException(f"Failed to save DSN to db: {e}") from e