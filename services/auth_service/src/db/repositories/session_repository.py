# services/auth_service/src/db/repositories/session_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from src.db.models.session_model import Session
from datetime import datetime, timedelta, timezone
from loguru import logger
from typing import Optional

# Определяем собственные исключения для репозитория
class SessionRepositoryError(Exception):
    """Базовое исключение для SessionRepository."""
    pass

class SessionCreationError(SessionRepositoryError):
    """Исключение при ошибке создания сессии."""
    pass

class SessionDeletionError(SessionRepositoryError):
    """Исключение при ошибке удаления сессии."""
    pass

class SessionNotFoundError(SessionRepositoryError):
    """Исключение, когда сессия не найдена."""
    pass

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, user_id: int, refresh_token: str) -> Session:
        """
        Создаёт новую сессию для пользователя с указанным refresh_token.

        Args:
            user_id (int): ID пользователя.
            refresh_token (str): Refresh токен.

        Returns:
            Session: Созданная сессия.

        Raises:
            ValueError: Если refresh_token пустой.
            SessionCreationError: При ошибке создания сессии.
        """
        if not refresh_token.strip():
            logger.error("Attempted to create session with an empty refresh token")
            raise ValueError("Refresh token cannot be empty")

        # Устанавливаем время истечения токена с учетом UTC
        expire_date = datetime.now(timezone.utc) + timedelta(days=7)
        new_session = Session(user_id=user_id, refresh_token=refresh_token, expires_at=expire_date)
        self.session.add(new_session)
        try:
            await self.session.commit()
            await self.session.refresh(new_session)
            logger.info(f"Session created for user_id={user_id} with refresh_token prefix={refresh_token[:10]}...")
            return new_session
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating session: {str(e)}")
            raise SessionCreationError("Failed to create session") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error creating session: {str(e)}")
            raise SessionCreationError("Failed to create session due to unexpected error") from e

    async def delete_session_by_token(self, refresh_token: str) -> bool:
        """
        Удаляет сессию по указанному refresh_token.

        Args:
            refresh_token (str): Refresh токен.

        Returns:
            bool: True если сессия удалена, False если не найдена.

        Raises:
            ValueError: Если refresh_token пустой.
            SessionDeletionError: При ошибке удаления сессии.
        """
        if not refresh_token.strip():
            logger.error("Attempted to delete session with an empty refresh token")
            raise ValueError("Refresh token cannot be empty")

        stmt = delete(Session).where(Session.refresh_token == refresh_token)
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            if result.rowcount > 0:
                logger.info(f"Session with refresh_token prefix={refresh_token[:10]}... deleted successfully")
                return True
            else:
                logger.warning(f"No session found with refresh_token prefix={refresh_token[:10]}...")
                return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error deleting session: {str(e)}")
            raise SessionDeletionError("Failed to delete session") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error deleting session: {str(e)}")
            raise SessionDeletionError("Failed to delete session due to unexpected error") from e

    async def get_session_by_token(self, refresh_token: str) -> Optional[Session]:
        """
        Получает сессию по refresh_token.

        Args:
            refresh_token (str): Refresh токен.

        Returns:
            Optional[Session]: Сессия или None, если не найдена.

        Raises:
            SessionRepositoryError: При ошибке доступа к данным.
        """
        stmt = select(Session).where(Session.refresh_token == refresh_token)
        try:
            result = await self.session.execute(stmt)
            session = result.scalar_one_or_none()
            if session:
                logger.debug(f"Found session for refresh_token prefix={refresh_token[:10]}...")
            else:
                logger.debug(f"No session found for refresh_token prefix={refresh_token[:10]}...")
            return session
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving session: {str(e)}")
            raise SessionRepositoryError("Failed to retrieve session") from e
        except Exception as e:
            logger.error(f"Unexpected error retrieving session: {str(e)}")
            raise SessionRepositoryError("Failed to retrieve session due to unexpected error") from e

    async def get_sessions_by_user_id(self, user_id: int) -> list[Session]:
        """
        Получает все сессии пользователя по user_id.

        Args:
            user_id (int): ID пользователя.

        Returns:
            list[Session]: Список сессий пользователя.

        Raises:
            SessionRepositoryError: При ошибке доступа к данным.
        """
        stmt = select(Session).where(Session.user_id == user_id)
        try:
            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            logger.debug(f"Found {len(sessions)} session(s) for user_id={user_id}")
            return sessions
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving sessions for user_id={user_id}: {str(e)}")
            raise SessionRepositoryError("Failed to retrieve sessions") from e
        except Exception as e:
            logger.error(f"Unexpected error retrieving sessions for user_id={user_id}: {str(e)}")
            raise SessionRepositoryError("Failed to retrieve sessions due to unexpected error") from e

    async def delete_all_sessions_for_user(self, user_id: int) -> int:
        """
        Удаляет все сессии для указанного пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            int: Количество удалённых сессий.

        Raises:
            SessionDeletionError: При ошибке удаления сессий.
        """
        stmt = delete(Session).where(Session.user_id == user_id)
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"Deleted {result.rowcount} session(s) for user_id={user_id}")
            return result.rowcount
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error deleting sessions for user_id={user_id}: {str(e)}")
            raise SessionDeletionError("Failed to delete sessions") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error deleting sessions for user_id={user_id}: {str(e)}")
            raise SessionDeletionError("Failed to delete sessions due to unexpected error") from e