from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session, check_db_connection
from src.api.schemas import HealthCheckResponse
from src.core.utils import handle_exceptions
from src.integrations.service_discovery import ServiceDiscoveryClient


class HealthController:
    def __init__(
            self,
            session: AsyncSession = Depends(get_session),
            service_discovery_client: ServiceDiscoveryClient = Depends(ServiceDiscoveryClient)
        ):
           self.session = session
           self.service_discovery_client = service_discovery_client


    @handle_exceptions
    async def health_check(self) -> HealthCheckResponse:
        """
        Performs a health check for the Data Storage Service.

        Checks database connection and if the service is registered in Service Discovery.
        Returns a status of "ok" if all checks pass, otherwise returns "error".
        """
        db_status = await check_db_connection(self.session)
        
        try:
           service_discovery_status = await self.service_discovery_client.check_service_registration()
        except Exception as e:
            service_discovery_status = False # Ставим False, чтобы сработала общая проверка

        if db_status and service_discovery_status:
             status_text = "ok"
             details_text = "Service is healthy and registered in Service Discovery"
        elif not db_status:
            status_text = "error"
            details_text = "Database connection failed"
        elif not service_discovery_status:
            status_text = "error"
            details_text = "Service is not registered in Service Discovery"   
        else:
           status_text = "error"
           details_text = "Service health check failed"    

        return HealthCheckResponse(status=status_text, details=details_text)