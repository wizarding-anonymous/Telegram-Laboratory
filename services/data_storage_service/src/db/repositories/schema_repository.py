from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Schema
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class SchemaRepository:
    """
    Repository for performing CRUD operations on the Schema model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, schema_data: Schema) -> Schema:
        """
        Creates a new schema in the database.
        """
        logger.info(f"Creating schema with data: {schema_data}")
        try:
            self.session.add(schema_data)
            await self.session.commit()
            await self.session.refresh(schema_data)
            logger.info(f"Schema created successfully. Schema id: {schema_data.id}")
            return schema_data
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            raise DatabaseException(f"Failed to create schema: {e}") from e

    @handle_exceptions
    async def get(self, schema_id: int) -> Optional[Schema]:
        """
        Retrieves a schema by its ID.
        """
        logger.info(f"Getting schema with ID: {schema_id}")
        try:
            query = select(Schema).where(Schema.id == schema_id)
            result = await self.session.execute(query)
            schema = result.scalar_one_or_none()
            if schema:
               logger.debug(f"Schema with ID {schema_id} found.")
            else:
               logger.warning(f"Schema with ID {schema_id} not found.")
            return schema
        except Exception as e:
             logger.error(f"Error getting schema {schema_id}: {e}")
             raise DatabaseException(f"Failed to get schema {schema_id}: {e}") from e

    @handle_exceptions
    async def get_by_bot_id(self, bot_id: int) -> Optional[Schema]:
        """
        Retrieves a schema by its bot ID.
        """
        logger.info(f"Getting schema by bot ID: {bot_id}")
        try:
          query = select(Schema).where(Schema.bot_id == bot_id)
          result = await self.session.execute(query)
          schema = result.scalar_one_or_none()
          if schema:
            logger.debug(f"Schema for bot {bot_id} found.")
          else:
            logger.warning(f"Schema for bot {bot_id} not found.")
          return schema
        except Exception as e:
             logger.error(f"Error getting schema by bot ID {bot_id}: {e}")
             raise DatabaseException(f"Failed to get schema by bot ID {bot_id}: {e}") from e

    @handle_exceptions
    async def delete(self, schema_id: int) -> None:
        """
        Deletes a schema by its ID.
        """
        logger.info(f"Deleting schema with ID: {schema_id}")
        try:
            query = delete(Schema).where(Schema.id == schema_id)
            await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Schema with ID {schema_id} deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting schema {schema_id}: {e}")
            raise DatabaseException(f"Failed to delete schema {schema_id}: {e}") from e

    @handle_exceptions
    async def get_all(self) -> List[Schema]:
        """
        Retrieves all schemas.
        """
        logger.info("Getting all schemas")
        try:
          query = select(Schema)
          result = await self.session.execute(query)
          schemas = list(result.scalars().all())
          logger.info(f"Found {len(schemas)} schemas.")
          return schemas
        except Exception as e:
           logger.error(f"Error getting all schemas: {e}")
           raise DatabaseException(f"Failed to get all schemas: {e}") from e