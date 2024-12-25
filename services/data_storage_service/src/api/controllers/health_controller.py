# services\data_storage_service\src\api\controllers\health_controller.py
from typing import Any, Dict

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.database import check_db_connection, check_migrations_status
from src.integrations.auth_service import AuthService
from src.integrations.telegram.client import TelegramClient


class HealthController:
    """
    Контроллер для выполнения проверки состояния микросервиса и его зависимостей.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация контроллера с сессией базы данных и другими зависимостями.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.session = session
        self.auth_service = AuthService()
        self.telegram_client = TelegramClient()

    @handle_exceptions
    async def check_health(self) -> Dict[str, Any]:
        """
        Выполнение полной проверки состояния микросервиса и его зависимостей.

        Проверяется доступность:
        - базы данных
        - Telegram API
        - Auth Service
        - Миграций для базы данных ботов

        Returns:
            Dict[str, Any]: Состояние сервиса и подробности о его зависимостях.

        Raises:
            HTTPException: В случае критических проблем с сервисом
        """
        logger.debug("Выполнение проверки состояния микросервиса")

        health_status = {
            "status": "healthy",
            "details": {
                "database": await self._check_database(),
                "telegram_api": await self._check_telegram_api(),
                "auth_service": await self._check_auth_service(),
                "migrations": await self._check_migrations(),
            },
            "version": "1.0.0",
        }

        if not all(
            detail["status"] == "healthy"
            for detail in health_status["details"].values()
        ):
            health_status["status"] = "degraded"
            logger.warning("Здоровье микросервиса деградировало")
        else:
            logger.info("Проверка состояния микросервиса прошла успешно")

        return health_status

    @handle_exceptions
    async def check_readiness(self) -> Dict[str, Any]:
        """
        Проверка готовности сервиса к обработке запросов.

        Returns:
            Dict[str, Any]: Статус готовности сервиса и детали проверки.

        Raises:
            HTTPException: Если сервис не готов к работе
        """
        logger.debug("Проверка готовности сервиса")

        readiness_status = {
            "status": "healthy",
            "details": {
                "database": await self._check_database(),
                "migrations": await self._check_migrations(),
            },
            "version": "1.0.0",
        }

        if not all(
            detail["status"] == "healthy"
            for detail in readiness_status["details"].values()
        ):
            readiness_status["status"] = "not_ready"
            logger.warning("Сервис не готов к работе")
            raise HTTPException(
                status_code=503,
                detail="Service is not ready"
            )

        logger.info("Сервис готов к работе")
        return readiness_status

    async def _check_database(self) -> Dict[str, str]:
        """
        Проверка состояния подключения к базе данных.

        Returns:
            Dict[str, str]: Статус здоровья базы данных и сообщение о подключении.
        """
        try:
            is_connected = await check_db_connection(self.session)
            if is_connected:
                return {
                    "status": "healthy",
                    "message": "Соединение с базой данных активно",
                }
            return {
                "status": "unhealthy",
                "message": "Ошибка подключения к базе данных",
            }
        except Exception as e:
            logger.error(f"Ошибка при проверке состояния базы данных: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Ошибка подключения к базе данных: {str(e)}",
            }

    async def _check_telegram_api(self) -> Dict[str, str]:
        """
        Проверка доступности Telegram API.

        Returns:
            Dict[str, str]: Статус доступности Telegram API и сообщение.
        """
        try:
            if await self.telegram_client.check_connection():
                return {"status": "healthy", "message": "Telegram API доступен"}
            return {
                "status": "unhealthy",
                "message": "Ошибка подключения к Telegram API",
            }
        except Exception as e:
            logger.error(f"Ошибка при проверке Telegram API: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Ошибка подключения к Telegram API: {str(e)}",
            }

    async def _check_auth_service(self) -> Dict[str, str]:
        """
        Проверка доступности Auth Service.

        Returns:
            Dict[str, str]: Статус доступности Auth Service и сообщение.
        """
        try:
            if await self.auth_service.check_health():
                return {"status": "healthy", "message": "Auth Service доступен"}
            return {
                "status": "unhealthy",
                "message": "Ошибка подключения к Auth Service",
            }
        except Exception as e:
            logger.error(f"Ошибка при проверке Auth Service: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Ошибка подключения к Auth Service: {str(e)}",
            }

    async def _check_migrations(self) -> Dict[str, str]:
        """
        Проверка состояния миграций для базы данных бота.

        Returns:
            Dict[str, str]: Статус здоровья миграций и сообщение.
        """
        try:
            migrations_status = await check_migrations_status(self.session)
            if migrations_status == "healthy":
                return {"status": "healthy", "message": "Миграции успешно применены"}
            return {"status": "unhealthy", "message": "Необходимо применить миграции"}
        except Exception as e:
            logger.error(f"Ошибка при проверке состояния миграций: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Ошибка при проверке состояния миграций: {str(e)}",
            }