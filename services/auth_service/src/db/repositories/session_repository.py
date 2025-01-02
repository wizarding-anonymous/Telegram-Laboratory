from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Session
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class SessionRepository:
    """
    Repository for performing CRUD operations on the Session model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, user_id: int, refresh_token: str, expires_at: datetime) -> Session:
        """
        Creates a new session in the database.
        """
        logger.info(f"Creating session for user_id: {user_id}")
        try:
            session = Session(user_id=user_id, refresh_token=refresh_token, expires_at=expires_at)
            self.session.add(session)
            await self.session.commit()
            await self.session.refresh(session)
            logger.info(f"Session created successfully with id: {session.id}")
            return session
        except Exception as e:
            logger.error(f"Error creating session for user_id: {user_id}. Error: {e}")
            raise DatabaseException(f"Failed to create session for user_id {user_id}: {e}") from e


    @handle_exceptions
    async def get(self, session_id: int) -> Optional[Session]:
        """
        Retrieves a session by its ID.
        """
        logger.info(f"Getting session with ID: {session_id}")
        try:
            query = select(Session).where(Session.id == session_id)
            result = await self.session.execute(query)
            session = result.scalar_one_or_none()
            if session:
                logger.debug(f"Session with ID {session_id} found")
            else:
                 logger.warning(f"Session with ID {session_id} not found")
            return session
        except Exception as e:
             logger.error(f"Error getting session with id {session_id}: {e}")
             raise DatabaseException(f"Failed to get session with id {session_id}: {e}") from e

    @handle_exceptions
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[Session]:
        """
        Retrieves a session by its refresh token.
        """
        logger.info(f"Getting session by refresh token")
        try:
           query = select(Session).where(Session.refresh_token == refresh_token)
           result = await self.session.execute(query)
           session = result.scalar_one_or_none()
           if session:
               logger.debug("Session found by refresh token.")
           else:
               logger.warning("Session not found by refresh token.")
           return session
        except Exception as e:
             logger.error(f"Error getting session by refresh token: {e}")
             raise DatabaseException(f"Failed to get session by refresh token: {e}") from e

    @handle_exceptions
    async def get_all(self) -> List[Session]:
        """
        Retrieves all sessions.
        """
        logger.info("Getting all sessions")
        try:
           query = select(Session)
           result = await self.session.execute(query)
           sessions = list(result.scalars().all())
           logger.debug(f"Found {len(sessions)} sessions.")
           return sessions
        except Exception as e:
            logger.error(f"Error getting all sessions: {e}")
            raise DatabaseException(f"Failed to get all sessions: {e}") from e

    @handle_exceptions
    async def delete(self, session_id: int) -> Optional[Session]:
        """
        Deletes a session by its ID.
        """
        logger.info(f"Deleting session with ID: {session_id}")
        try:
            query = delete(Session).where(Session.id == session_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Session with id {session_id} deleted successfully")
            return result.scalar_one_or_none()
        except Exception as e:
             logger.error(f"Error deleting session with ID: {session_id}: {e}")
             raise DatabaseException(f"Failed to delete session with id {session_id}: {e}") from e
    
    @handle_exceptions
    async def delete_by_refresh_token(self, refresh_token: str) -> None:
        """
        Deletes a session by refresh token.
        """
        logger.info(f"Deleting session with refresh token")
        try:
           query = delete(Session).where(Session.refresh_token == refresh_token)
           await self.session.execute(query)
           await self.session.commit()
           logger.info(f"Session with refresh token {refresh_token} deleted successfully")
        except Exception as e:
           logger.error(f"Error deleting session by refresh token: {e}")
           raise DatabaseException(f"Failed to delete session by refresh token {refresh_token}: {e}") from e