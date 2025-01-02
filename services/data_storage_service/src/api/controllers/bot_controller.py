from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.api.schemas.bot_schema import BotCreate, BotResponse, BotUpdate
from src.api.schemas.response_schema import ErrorResponse, SuccessResponse
from src.core.database_manager import DatabaseManager
from src.core.utils import handle_exceptions
from src.core.utils.validators import validate_bot_name
from src.db.database import  get_session
from src.db.repositories.bot_repository import BotRepository
from src.db.repositories.schema_repository import SchemaRepository
from src.integrations.auth_service import AuthService

router = APIRouter(
    prefix="/meta/bots",
    tags=["Bots"],
    responses={404: {"model": ErrorResponse, "description": "Not Found"}},
)


class BotController:
    """
    Контроллер для работы с записями о ботах в мета-базе данных.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """
        Инициализация контроллера с сессией базы данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.session = session
        self.bot_repository = BotRepository(session)
        self.schema_repository = SchemaRepository(session)
        self.auth_service = AuthService()
        self.db_manager = DatabaseManager()


    @handle_exceptions
    async def create_bot(self, bot_data: BotCreate, user_id: int) -> BotResponse:
        """
        Создание нового бота в мета-базе данных.

        Args:
            bot_data (BotCreate): Данные для создания бота.
            user_id (int): ID пользователя, который создает бота.

        Returns:
            BotResponse: Ответ с информацией о созданном боте.
        """
        logger.info(f"Creating new bot for user {user_id}")

        # Проверка прав доступа пользователя для создания бота
        await self.auth_service.validate_user_permissions(user_id, "create_bot")

        # Валидация имени бота
        validate_bot_name(bot_data.name)

        # Создание записи о боте в мета-базе данных
        bot = await self.bot_repository.create(bot_data.dict(), user_id)

        # Создание базы данных для бота и запуск миграций
        try:
            # Создание базы данных и применение миграций
             dsn = await self.db_manager.create_bot_database(bot_id=bot.id, schema_repository=self.schema_repository)
        except Exception as e:
            logger.error(
                f"Error creating database or applying migrations for bot {bot.id}: {e}"
            )
            raise HTTPException(
                status_code=500, detail="Error creating database for bot"
            )

        logger.info(f"Bot {bot.id} successfully created for user {user_id}")
        return BotResponse.from_orm(bot)

    @handle_exceptions
    async def get_bot(self, bot_id: int, user_id: int) -> BotResponse:
        """
        Получение информации о боте по его ID.

        Args:
            bot_id (int): ID бота.
            user_id (int): ID пользователя.

        Returns:
            BotResponse: Ответ с информацией о боте.
        """
        logger.info(
            f"Requesting information about bot with ID {bot_id} for user {user_id}"
        )

        # Проверка прав доступа пользователя для чтения информации о боте
        await self.auth_service.validate_user_permissions(user_id, "read_bot")

        # Получение записи о боте
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        if bot.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this bot"
            )

        return BotResponse.from_orm(bot)

    @handle_exceptions
    async def update_bot(
        self, bot_id: int, bot_data: BotUpdate, user_id: int
    ) -> BotResponse:
        """
        Обновление данных о боте.

        Args:
            bot_id (int): ID бота.
            bot_data (BotUpdate): Данные для обновления.
            user_id (int): ID пользователя.

        Returns:
            BotResponse: Ответ с обновленной информацией о боте.
        """
        logger.info(
            f"Updating information about bot with ID {bot_id} for user {user_id}"
        )

        # Проверка прав доступа пользователя для обновления данных о боте
        await self.auth_service.validate_user_permissions(user_id, "update_bot")

        # Получение текущей записи о боте
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        if bot.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this bot"
            )

        # Обновление данных бота
        updated_bot = await self.bot_repository.update(
            bot_id, bot_data.dict(exclude_unset=True)
        )

        logger.info(
            f"Data about bot with ID {bot_id} successfully updated for user {user_id}"
        )
        return BotResponse.from_orm(updated_bot)

    @handle_exceptions
    async def delete_bot(self, bot_id: int, user_id: int) -> SuccessResponse:
        """
        Удаление записи о боте.

        Args:
            bot_id (int): ID бота.
            user_id (int): ID пользователя.

        Returns:
            SuccessResponse: Сообщение об успешном удалении.
        """
        logger.info(f"Deleting bot with ID {bot_id} for user {user_id}")

        # Проверка прав доступа пользователя для удаления бота
        await self.auth_service.validate_user_permissions(user_id, "delete_bot")

        # Получение записи о боте
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        if bot.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this bot"
            )

        # Удаление бота и базы данных
        try:
            await self.db_manager.delete_bot_database(bot_id=bot_id, schema_repository=self.schema_repository)
            deleted = await self.bot_repository.delete(bot_id)
            if not deleted:
               raise HTTPException(
                status_code=404, detail="Bot not found or already deleted"
            )

        except Exception as e:
              logger.error(f"Error deleting database for bot {bot_id}: {e}")
              raise HTTPException(
                  status_code=500, detail="Error deleting database for bot"
              )

        logger.info(f"Bot with ID {bot_id} successfully deleted for user {user_id}")
        return SuccessResponse(message="Bot deleted successfully")


# Роуты для API
@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Создание нового бота для пользователя.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = BotController(session)
    return await controller.create_bot(bot_data, user_id)


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Получение информации о боте по его ID.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = BotController(session)
    return await controller.get_bot(bot_id, user_id)


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdate,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Обновление данных о боте.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = BotController(session)
    return await controller.update_bot(bot_id, bot_data, user_id)


@router.delete("/{bot_id}", response_model=SuccessResponse)
async def delete_bot(
    bot_id: int,
    user: dict = Depends(get_current_user),  # Получаем текущего пользователя из токена
    session: AsyncSession = Depends(get_session),
):
    """
    Удаление бота по его ID.
    """
    user_id = user["user_id"]  # Получаем ID пользователя из токена
    controller = BotController(session)
    return await controller.delete_bot(bot_id, user_id)