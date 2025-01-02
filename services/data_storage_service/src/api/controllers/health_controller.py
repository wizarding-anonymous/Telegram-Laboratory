from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session, check_db_connection
from src.api.schemas import HealthCheckResponse
from src.core.utils import handle_exceptions


class HealthController:
    def __init__(
            self,
            session: AsyncSession = Depends(get_session),
        ):
           self.session = session


    @handle_exceptions
    async def health_check(self) -> HealthCheckResponse:
        """
        Performs a health check for the Data Storage Service.

        Checks database connection.
        Returns a status of "ok" if the database connection is healthy, otherwise returns "error".
        """
        logger.info("Performing health check...")
        try:
            db_status = await check_db_connection(self.session)
            if db_status:
                logger.info("Database connection is healthy.")
                return HealthCheckResponse(
                    status="ok", details="Service is healthy and database connection is OK"
                )
            else:
                logger.error("Database connection failed.")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database connection failed",
                )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service health check failed: {str(e)}",
            ) from e