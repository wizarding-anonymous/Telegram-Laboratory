from typing import List, Optional
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from datetime import datetime

from src.db.models import Log
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class LogRepository:
    """
    Repository for performing CRUD operations on the Log model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, level: str, service: str, message: str, timestamp: datetime, metadata: Optional[dict] = None) -> Log:
        """
        Creates a new log entry in the database.
        """
        logger.info(f"Creating log entry: level={level}, service={service}")
        try:
            log = Log(level=level, service=service, message=message, timestamp=timestamp, metadata=metadata)
            self.session.add(log)
            await self.session.commit()
            await self.session.refresh(log)
            logger.info(f"Log entry created successfully with id: {log.id}")
            return log
        except Exception as e:
            logger.error(f"Failed to create log entry: {e}")
            raise DatabaseException(f"Failed to create log entry: {e}") from e


    @handle_exceptions
    async def get(self, log_id: int) -> Optional[Log]:
        """
        Retrieves a log entry by its ID.
        """
        logger.info(f"Getting log with ID: {log_id}")
        try:
            query = select(Log).where(Log.id == log_id)
            result = await self.session.execute(query)
            log = result.scalar_one_or_none()
            if log:
                logger.debug(f"Log with ID {log_id} found.")
            else:
                logger.warning(f"Log with ID {log_id} not found.")
            return log
        except Exception as e:
            logger.error(f"Error getting log with ID {log_id}: {e}")
            raise DatabaseException(f"Failed to get log with id {log_id}: {e}") from e

    @handle_exceptions
    async def get_all(self, level: Optional[str] = None, service: Optional[str] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Log]:
        """
        Retrieves all log entries based on filters.
        """
        logger.info(f"Getting all logs with filters: level={level}, service={service}, start_time={start_time}, end_time={end_time}")
        try:
            query = select(Log)
            conditions = []
            if level:
              conditions.append(Log.level == level)
            if service:
              conditions.append(Log.service == service)
            if start_time:
               conditions.append(Log.timestamp >= start_time)
            if end_time:
               conditions.append(Log.timestamp <= end_time)
            if conditions:
                 query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            logs = list(result.scalars().all())
            logger.debug(f"Found {len(logs)} logs with provided filters")
            return logs
        except Exception as e:
            logger.error(f"Error getting all logs: {e}")
            raise DatabaseException(f"Failed to get all logs: {e}") from e


    @handle_exceptions
    async def delete(self, log_id: int) -> Optional[Log]:
         """
         Deletes a log by its ID.
         """
         logger.info(f"Deleting log with ID: {log_id}")
         try:
            query = delete(Log).where(Log.id == log_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Log with ID {log_id} deleted successfully")
            return result.scalar_one_or_none()
         except Exception as e:
            logger.error(f"Error deleting log with ID {log_id}: {e}")
            raise DatabaseException(f"Failed to delete log with id {log_id}: {e}") from e