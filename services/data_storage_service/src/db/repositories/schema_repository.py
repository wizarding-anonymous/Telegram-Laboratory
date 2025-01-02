from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

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
        self.session.add(schema_data)
        await self.session.commit()
        await self.session.refresh(schema_data)
        return schema_data

    @handle_exceptions
    async def get(self, schema_id: int) -> Optional[Schema]:
        """
        Retrieves a schema by its ID.
        """
        query = select(Schema).where(Schema.id == schema_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    @handle_exceptions
    async def get_by_bot_id(self, bot_id: int) -> Optional[Schema]:
        """
        Retrieves a schema by its bot ID.
        """
        query = select(Schema).where(Schema.bot_id == bot_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    @handle_exceptions
    async def delete(self, schema_id: int) -> None:
        """
        Deletes a schema by its ID.
        """
        query = delete(Schema).where(Schema.id == schema_id)
        await self.session.execute(query)
        await self.session.commit()