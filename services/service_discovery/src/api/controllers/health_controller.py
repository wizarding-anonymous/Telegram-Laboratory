from typing import Dict
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.api.schemas import HealthCheckResponse
from src.core.utils import handle_exceptions
from src.db.database import get_session, check_db_connection
from src.integrations.logging_client import LoggingClient
from src.config import settings


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class HealthController:
    """
    Controller for performing health checks of the service and its dependencies.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    @handle_exceptions
    async def check_health(self) -> HealthCheckResponse:
        """
        Performs a health check of the service and its dependencies.
        Checks database connection and reports status.
        """
        logging_client.info("Performing health check...")
        try:
            db_connected = await check_db_connection(self.session)
            if db_connected:
                logging_client.info("Database connection is healthy.")
                return HealthCheckResponse(
                    status="ok", details="Service is healthy and database connection is OK"
                )
            else:
                logging_client.error("Database connection failed.")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database connection failed",
                )
        except Exception as e:
            logging_client.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service health check failed: {str(e)}",
            ) from e