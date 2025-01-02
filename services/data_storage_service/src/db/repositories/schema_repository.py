from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.exceptions import DatabaseException
from src.db.models.schema_model import Schema


class SchemaRepository:
    """
    Repository for performing CRUD operations on the Schema model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, bot_id: int, dsn: str) -> Schema:
        """Creates a new schema entry."""
        try:
            new_schema = Schema(bot_id=bot_id, dsn=dsn)
            self.session.add(new_schema)
            await self.session.commit()
            await self.session.refresh(new_schema)
            return new_schema
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Error creating schema: {e}") from e

    async def get_by_bot_id(self, bot_id: int) -> Optional[Schema]:
        """Retrieves a schema by its bot ID."""
        try:
            query = select(Schema).where(Schema.bot_id == bot_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Error getting schema by bot ID {bot_id}: {e}") from e

    async def get_all(self) -> List[Schema]:
        """Retrieves all schema entries."""
        try:
           query = select(Schema)
           result = await self.session.execute(query)
           return list(result.scalars().all())
        except Exception as e:
            raise DatabaseException(f"Error getting all schemas: {e}") from e


    async def update(self, schema_id: int, dsn: str) -> Optional[Schema]:
        """Updates a schema's DSN by schema ID."""
        try:
            query = select(Schema).where(Schema.id == schema_id)
            result = await self.session.execute(query)
            schema = result.scalar_one_or_none()
            if schema:
                schema.dsn = dsn
                await self.session.commit()
                await self.session.refresh(schema)
                return schema
            return None
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Error updating schema with ID {schema_id}: {e}") from e


    async def delete_by_bot_id(self, bot_id: int) -> None:
        """Deletes a schema by its bot ID."""
        try:
             query = select(Schema).where(Schema.bot_id == bot_id)
             result = await self.session.execute(query)
             schema = result.scalar_one_or_none()
             if schema:
                await self.session.delete(schema)
                await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Error deleting schema by bot ID {bot_id}: {e}") from e


    async def delete(self, schema_id: int) -> None:
        """Deletes a schema by its ID."""
        try:
            query = select(Schema).where(Schema.id == schema_id)
            result = await self.session.execute(query)
            schema = result.scalar_one_or_none()
            if schema:
                await self.session.delete(schema)
                await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Error deleting schema with ID {schema_id}: {e}") from e