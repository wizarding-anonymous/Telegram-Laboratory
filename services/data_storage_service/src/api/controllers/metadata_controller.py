from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.api.schemas.metadata_schema import (
    MetadataCreate,
    MetadataResponse,
    MetadataUpdate,
)
from src.api.schemas.response_schema import ErrorResponse, SuccessResponse
from src.core.utils import handle_exceptions
from src.core.utils.validators import validate_metadata_key
from src.db.database import get_session
from src.db.repositories.metadata_repository import MetadataRepository
from src.db.repositories.schema_repository import SchemaRepository
from src.integrations.auth_service import AuthService
from src.core.database_manager import DatabaseManager

router = APIRouter(
    prefix="/meta/metadata",
    tags=["Metadata"],
    responses={404: {"model": ErrorResponse, "description": "Not Found"}},
)


class MetadataController:
    """
    Контроллер для работы с метаданными ботов.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """
        Инициализация контроллера с сессией базы данных и другими зависимостями.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.session = session
        self.metadata_repository = MetadataRepository(session)
        self.schema_repository = SchemaRepository(session)
        self.auth_service = AuthService()
        self.db_manager = DatabaseManager()

    @handle_exceptions
    async def create_metadata(
        self, metadata_data: MetadataCreate, user_id: int
    ) -> MetadataResponse:
        """
        Создание метаданных для бота.

        Args:
            metadata_data (MetadataCreate): Данные для создания метаданных.
            user_id (int): ID пользователя, который создает метаданные.

        Returns:
            MetadataResponse: Ответ с информацией о созданных метаданных.
        """
        logger.info(f"Creating metadata for bot for user {user_id}")

        # Проверка прав доступа пользователя для создания метаданных
        await self.auth_service.validate_user_permissions(user_id, "create_metadata")

        # Валидация ключа метаданных
        validate_metadata_key(metadata_data.key)


        # Создание записи о метаданных
        metadata = await self.metadata_repository.create(
            metadata_data.dict(), user_id
        )

        logger.info(
            f"Metadata for bot successfully created for user {user_id}"
        )
        return MetadataResponse.from_orm(metadata)

    @handle_exceptions
    async def get_metadata(self, bot_id: int, user_id: int) -> MetadataResponse:
        """
        Получение информации о метаданных для конкретного бота.

        Args:
            bot_id (int): ID бота.
            user_id (int): ID пользователя.

        Returns:
            MetadataResponse: Ответ с информацией о метаданных.
        """
        logger.info(
            f"Requesting metadata information for bot with ID {bot_id} for user {user_id}"
        )

        # Проверка прав доступа пользователя для чтения метаданных
        await self.auth_service.validate_user_permissions(user_id, "read_metadata")

        # Получение метаданных
        metadata = await self.metadata_repository.get_by_bot_id(bot_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")

        # Проверка владельца бота
        if metadata.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this metadata"
            )

        return MetadataResponse.from_orm(metadata)

    @handle_exceptions
    async def update_metadata(
        self, bot_id: int, metadata_data: MetadataUpdate, user_id: int
    ) -> MetadataResponse:
        """
        Обновление метаданных для конкретного бота.

        Args:
            bot_id (int): ID бота.
            metadata_data (MetadataUpdate): Данные для обновления метаданных.
            user_id (int): ID пользователя.

        Returns:
            MetadataResponse: Ответ с обновленной информацией о метаданных.
        """
        logger.info(
            f"Updating metadata for bot with ID {bot_id} for user {user_id}"
        )

        # Проверка прав доступа пользователя для обновления метаданных
        await self.auth_service.validate_user_permissions(user_id, "update_metadata")

        # Получение текущих метаданных
        metadata = await self.metadata_repository.get_by_bot_id(bot_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")

        if metadata.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this metadata"
            )

        # Обновление метаданных
        updated_metadata = await self.metadata_repository.update(
            bot_id, metadata_data.dict(exclude_unset=True)
        )

        logger.info(
            f"Metadata for bot with ID {bot_id} successfully updated for user {user_id}"
        )
        return MetadataResponse.from_orm(updated_metadata)

    @handle_exceptions
    async def delete_metadata(self, bot_id: int, user_id: int) -> SuccessResponse:
        """
        Удаление метаданных для бота.

        Args:
            bot_id (int): ID бота.
            user_id (int): ID пользователя.

        Returns:
            SuccessResponse: Сообщение об успешном удалении метаданных.
        """
        logger.info(
            f"Deleting metadata for bot with ID {bot_id} for user {user_id}"
        )

        # Проверка прав доступа пользователя для удаления метаданных
        await self.auth_service.validate_user_permissions(user_id, "delete_metadata")

        # Получение метаданных
        metadata = await self.metadata_repository.get_by_bot_id(bot_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")

        if metadata.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this metadata"
            )

        # Удаление метаданных
        deleted = await self.metadata_repository.delete(bot_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Metadata not found or already deleted"
            )

        logger.info(
            f"Metadata for bot with ID {bot_id} successfully deleted for user {user_id}"
        )
        return SuccessResponse(message="Metadata deleted successfully")


# Роуты для API
@router.post("/", response_model=MetadataResponse, status_code=status.HTTP_201_CREATED)
async def create_metadata(
    metadata_data: MetadataCreate,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Создание метаданных для бота.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = MetadataController(session)
    return await controller.create_metadata(metadata_data, user_id)


@router.get("/{bot_id}", response_model=MetadataResponse)
async def get_metadata(
    bot_id: int,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Получение метаданных для бота.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = MetadataController(session)
    return await controller.get_metadata(bot_id, user_id)


@router.put("/{bot_id}", response_model=MetadataResponse)
async def update_metadata(
    bot_id: int,
    metadata_data: MetadataUpdate,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Обновление метаданных для бота.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = MetadataController(session)
    return await controller.update_metadata(bot_id, metadata_data, user_id)


@router.delete("/{bot_id}", response_model=SuccessResponse)
async def delete_metadata(
    bot_id: int,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Удаление метаданных для бота.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = MetadataController(session)
    return await controller.delete_metadata(bot_id, user_id)