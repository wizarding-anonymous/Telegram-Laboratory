from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.repositories import SchemaRepository
from src.api.schemas import (
    SuccessResponse,
    ErrorResponse,
    SchemaResponse,
    SchemaCreate,
    SchemaListResponse
)
from src.core.utils import handle_exceptions
from src.integrations.auth_service.client import get_current_user
from src.core.database_manager import DatabaseManager


class SchemaController:
    def __init__(
            self,
            session: AsyncSession = Depends(get_session),
            database_manager: DatabaseManager = Depends(DatabaseManager)
    ):
        self.repository = SchemaRepository(session)
        self.database_manager = database_manager

    @handle_exceptions
    async def get_schema(self, bot_id: int, current_user: dict = Depends(get_current_user)) -> SchemaResponse:
        """
        Retrieves the database schema for a bot by its ID.
        If the schema does not exist, it creates a new database for the bot, and then retrieves the schema.
        """
        logger.info(f"Getting schema for bot ID: {bot_id}")
        try:
            schema = await self.repository.get_by_bot_id(bot_id)
            if not schema:
                logger.warning(f"Schema for bot ID {bot_id} not found. Creating new database.")
                dsn = await self.database_manager.create_database_for_bot(bot_id, current_user['id']) # Если схемы нет, создадим новую базу данных, а затем схему
                if not dsn:
                     logger.error(f"Failed to create database for bot {bot_id}")
                     raise HTTPException(
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Failed to create database for bot with ID {bot_id}",
                      )
                schema = await self.repository.get_by_bot_id(bot_id) # Получим схему снова после создания БД
                if not schema:
                     logger.error(f"Schema for bot {bot_id} not found after database creation")
                     raise HTTPException(
                         status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Schema for bot with ID {bot_id} not found after database creation",
                    )
                logger.info(f"Schema and database created for bot ID {bot_id}. Schema: {schema}")

            schema_response =  SchemaResponse(id=schema.id, bot_id=schema.bot_id, dsn=schema.dsn, created_at=schema.created_at)
            logger.info(f"Schema retrieved successfully: {schema_response}")
            return schema_response
        except Exception as e:
          logger.error(f"Error getting schema for bot {bot_id}: {e}")
          raise

    @handle_exceptions
    async def delete_schema(self, bot_id: int, current_user: dict = Depends(get_current_user)) -> SuccessResponse:
        """
        Deletes the database schema for a bot by its ID.
        """
        logger.info(f"Deleting schema for bot ID: {bot_id}")
        try:
            schema = await self.repository.get_by_bot_id(bot_id)
            if not schema:
                logger.warning(f"Schema for bot with ID {bot_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Schema for bot with ID {bot_id} not found",
                )
            await self.database_manager.delete_database_for_bot(bot_id)
            logger.info(f"Database for bot {bot_id} deleted")
            await self.repository.delete(schema.id)
            logger.info(f"Schema with ID {schema.id} deleted successfully")
            return SuccessResponse(message="Schema and database deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting schema for bot {bot_id}: {e}")
            raise

    @handle_exceptions
    async def create_schema(self, schema_data: SchemaCreate, current_user: dict = Depends(get_current_user)) -> SchemaResponse:
      """
      Creates a new schema for a bot.
      """
      logger.info(f"Creating schema with data: {schema_data}")
      try:
        schema = await self.repository.create(**schema_data.model_dump())
        logger.info(f"Schema created successfully. Schema: {schema}")
        return SchemaResponse(**schema.__dict__)
      except Exception as e:
        logger.error(f"Error creating schema: {e}")
        raise
    
    @handle_exceptions
    async def get_all_schemas(self, current_user: dict = Depends(get_current_user)) -> SchemaListResponse:
      """
      Retrieves all schemas.
      """
      logger.info(f"Getting all schemas")
      try:
          schemas = await self.repository.get_all()
          logger.info(f"Found {len(schemas)} schemas")
          return SchemaListResponse(items=[SchemaResponse(**schema.__dict__) for schema in schemas])
      except Exception as e:
         logger.error(f"Error getting all schemas {e}")
         raise