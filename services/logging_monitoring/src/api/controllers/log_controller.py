from typing import List
from fastapi import Depends, HTTPException, status, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.log_manager import LogManager
from src.api.schemas import (
    LogCreate,
    LogResponse,
    LogListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.api.middleware.auth import admin_required
from src.db.database import get_session

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class LogController:
    """
    Controller for managing logs in the Logging and Monitoring service.
    """

    def __init__(self, log_manager: LogManager = Depends(), session: AsyncSession = Depends(get_session)):
        self.log_manager = log_manager
        self.session = session

    @handle_exceptions
    async def create_log(self, log_data: LogCreate, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Creates a new log entry.
        """
        logging_client.info(f"Creating log entry: {log_data}")
        try:
             await self.log_manager.create_log(**log_data.model_dump())
             logging_client.info("Log entry created successfully.")
             return SuccessResponse(message="Log entry created successfully")
        except Exception as e:
            logging_client.error(f"Failed to create log entry: {e}")
            raise

    @handle_exceptions
    async def get_logs(
        self,
        level: str = Query(None),
        service: str = Query(None),
        start_time: str = Query(None),
        end_time: str = Query(None),
        user: dict = Depends(admin_required),
    ) -> LogListResponse:
        """
        Retrieves logs based on filters.
        """
        logging_client.info(f"Getting logs with level: {level}, service: {service}, start_time: {start_time}, end_time: {end_time}")
        try:
            logs = await self.log_manager.get_logs(
                 level=level, service=service, start_time=start_time, end_time=end_time
            )
            logging_client.info(f"Successfully retrieved {len(logs)} logs.")
            return LogListResponse(items=[LogResponse(**log.__dict__) for log in logs])
        except Exception as e:
           logging_client.error(f"Failed to get logs: {e}")
           raise

    @handle_exceptions
    async def get_all_logs(self, user: dict = Depends(admin_required)) -> LogListResponse:
        """
        Retrieves a list of all logs.
        """
        logging_client.info("Getting all logs")
        try:
            logs = await self.log_manager.get_all_logs()
            logging_client.info(f"Successfully retrieved {len(logs)} logs")
            return LogListResponse(items=[LogResponse(**log.__dict__) for log in logs])
        except Exception as e:
            logging_client.error(f"Failed to get all logs: {e}")
            raise