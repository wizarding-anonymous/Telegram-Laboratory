from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session
from src.db.repositories import LogRepository
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException
from src.integrations.logging_client import LoggingClient
from src.config import settings
from datetime import datetime

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class LogManager:
    """
    Manages log entries in the Logging and Monitoring service.
    """

    def __init__(self, log_repository: LogRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = log_repository
        self.session = session

    @handle_exceptions
    async def create_log(self, level: str, service: str, message: str, timestamp: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Creates a new log entry.
        """
        logging_client.info(f"Creating log entry: level={level}, service={service}")
        try:
            if timestamp:
                formatted_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                formatted_timestamp = datetime.utcnow()
            await self.repository.create(
                 level=level, service=service, message=message, timestamp=formatted_timestamp, metadata=metadata
            )
            logging_client.info("Log entry created successfully.")
        except Exception as e:
            logging_client.error(f"Error creating log entry: {e}")
            raise

    @handle_exceptions
    async def get_log(self, log_id: int) -> Optional[Dict[str, Any]]:
         """
         Retrieves a log entry by its ID.
         """
         logging_client.info(f"Getting log with ID: {log_id}")
         try:
              log = await self.repository.get(log_id=log_id)
              if not log:
                  logging_client.warning(f"Log with ID {log_id} not found")
                  raise HTTPException(
                      status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
                   )
              logging_client.info(f"Log with id {log_id} retrieved successfully")
              return log.__dict__
         except Exception as e:
           logging_client.error(f"Error getting log by id {log_id}: {e}")
           raise

    @handle_exceptions
    async def get_logs(self, level: Optional[str] = None, service: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
      """
      Retrieves logs based on filters.
      """
      logging_client.info(f"Getting logs with filters: level={level}, service={service}, start_time={start_time}, end_time={end_time}")
      try:
         if start_time:
            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
         if end_time:
             end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

         logs = await self.repository.get_all(level=level, service=service, start_time=start_time, end_time=end_time)
         logging_client.info(f"Retrieved {len(logs)} logs with provided filters.")
         return [log.__dict__ for log in logs]
      except Exception as e:
          logging_client.error(f"Error getting logs with filters, {e}")
          raise

    @handle_exceptions
    async def get_all_logs(self) -> List[Dict[str, Any]]:
        """
        Retrieves all logs.
        """
        logging_client.info("Getting all logs")
        try:
          logs = await self.repository.get_all()
          logging_client.info(f"Successfully retrieved {len(logs)} logs")
          return [log.__dict__ for log in logs]
        except Exception as e:
             logging_client.error(f"Error getting all logs: {e}")
             raise