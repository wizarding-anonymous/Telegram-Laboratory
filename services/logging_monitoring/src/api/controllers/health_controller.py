from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session, check_db_connection
from src.api.schemas import HealthCheckResponse
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.integrations.prometheus_client import PrometheusClient
from src.integrations.auth_service.client import AuthService

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class HealthController:
    """
    Controller for performing health checks of the service and its dependencies.
    """

    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        prometheus_client: PrometheusClient = Depends(PrometheusClient),
        auth_service: AuthService = Depends(AuthService)
    ):
        self.session = session
        self.prometheus_client = prometheus_client
        self.auth_service = auth_service

    @handle_exceptions
    async def check_health(self) -> HealthCheckResponse:
        """
        Performs a health check of the service and its dependencies.
        Checks database connection, prometheus and auth service.
        Returns a status of "ok" if all components are healthy, otherwise returns an "error" status
        with details of the failing services.
        """
        logging_client.info("Performing health check...")
        health_status = {"database": False, "prometheus": False, "auth_service": False}
        try:
            db_connected = await check_db_connection(self.session)
            if db_connected:
                logging_client.debug("Database connection is healthy.")
                health_status["database"] = True
            else:
                logging_client.error("Database connection failed.")
        
            prometheus_connected = await self.prometheus_client.check_connection()
            if prometheus_connected:
                logging_client.debug("Prometheus connection is healthy.")
                health_status["prometheus"] = True
            else:
                logging_client.error("Prometheus connection failed.")

            auth_service_connected = await self.auth_service.check_health()
            if auth_service_connected:
                 logging_client.debug("Auth service connection is healthy.")
                 health_status["auth_service"] = True
            else:
                logging_client.error("Auth service connection failed.")
           

            if all(health_status.values()):
                 logging_client.info("Health check passed all checks.")
                 return HealthCheckResponse(
                       status="ok", details="Service is healthy and all dependencies are operational."
                )

            else:
                logging_client.error(f"Health check failed, details: {health_status}")
                failed_services = [service for service, status in health_status.items() if not status]
                raise HTTPException(
                      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                      detail=f"Service health check failed. Following services are not healthy: {failed_services}",
                )
        except Exception as e:
            logging_client.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service health check failed: {str(e)}",
            ) from e