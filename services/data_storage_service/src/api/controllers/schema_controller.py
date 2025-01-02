from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session
from src.db.repositories import SchemaRepository
from src.api.schemas import (
    SuccessResponse,
    ErrorResponse,
    SchemaResponse,
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
        """
        
        schema = await self.repository.get_by_bot_id(bot_id)
       
        if not schema:
           
            dsn = await self.database_manager.create_database_for_bot(bot_id, current_user['id']) # Если схемы нет, создадим новую базу данных, а затем схему
            
            if not dsn:
                 raise HTTPException(
                       status_code=status.HTTP_404_NOT_FOUND,
                       detail=f"Schema for bot with ID {bot_id} not found",
                   )
            
            schema = await self.repository.get_by_bot_id(bot_id) # Получим схему снова после создания БД
            
            if not schema:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Schema for bot with ID {bot_id} not found",
                )

        return SchemaResponse(id=schema.id, bot_id=schema.bot_id, dsn=schema.dsn, created_at=schema.created_at)



    @handle_exceptions
    async def delete_schema(self, bot_id: int, current_user: dict = Depends(get_current_user)) -> SuccessResponse:
        """
        Deletes the database schema for a bot by its ID.
        """
        schema = await self.repository.get_by_bot_id(bot_id)
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema for bot with ID {bot_id} not found",
            )
        await self.database_manager.delete_database_for_bot(bot_id)
        await self.repository.delete(schema.id)
        return SuccessResponse(message="Schema and database deleted successfully")