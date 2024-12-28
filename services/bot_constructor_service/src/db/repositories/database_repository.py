from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.models.database_model import Database
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class DatabaseRepository:
    """
    Repository for performing database operations on database entities.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the DatabaseRepository with a database session."""
        self.session = session
        logging_client.info("DatabaseRepository initialized")

    @handle_exceptions
    async def create(self, database_data: dict) -> Database:
        """Creates a new database block in the database."""
        logging_client.info(f"Creating new database block with data: {database_data}")
        database = Database(**database_data)
        self.session.add(database)
        await self.session.commit()
        await self.session.refresh(database)
        logging_client.info(f"Database block with id: {database.id} created successfully")
        return database

    @handle_exceptions
    async def get_by_id(self, database_id: int) -> Optional[Database]:
        """Retrieves a database block by its ID."""
        logging_client.info(f"Getting database block by id: {database_id}")
        database = await self.session.get(Database, database_id)
        if database:
            logging_client.info(f"Database block with id: {database_id} retrieved successfully")
        else:
            logging_client.warning(f"Database block with id: {database_id} not found")
        return database

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[Database]:
        """Retrieves all database blocks for a specific bot."""
        logging_client.info(f"Getting all database blocks for bot_id: {bot_id}")
        query = select(Database).where(Database.bot_id == bot_id)
        result = await self.session.execute(query)
        databases = result.scalars().all()
        logging_client.info(f"Found {len(databases)} database blocks for bot_id: {bot_id}")
        return list(databases)

    @handle_exceptions
    async def update(self, database_id: int, database_data: dict) -> Optional[Database]:
        """Updates an existing database block."""
        logging_client.info(f"Updating database block with id: {database_id} with data: {database_data}")
        database = await self.session.get(Database, database_id)
        if database:
            for key, value in database_data.items():
                setattr(database, key, value)
            await self.session.commit()
            await self.session.refresh(database)
            logging_client.info(f"Database block with id: {database_id} updated successfully")
            return database
        logging_client.warning(f"Database block with id: {database_id} not found for update")
        return None

    @handle_exceptions
    async def delete(self, database_id: int) -> bool:
        """Deletes a database block by its ID."""
        logging_client.info(f"Deleting database block with id: {database_id}")
        database = await self.session.get(Database, database_id)
        if database:
            await self.session.delete(database)
            await self.session.commit()
            logging_client.info(f"Database block with id: {database_id} deleted successfully")
            return True
        logging_client.warning(f"Database block with id: {database_id} not found for delete")
        return False