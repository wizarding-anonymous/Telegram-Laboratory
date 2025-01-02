import httpx
from fastapi import HTTPException, status
from src.config import settings
from src.core.utils import handle_exceptions


class ServiceDiscoveryClient:
    def __init__(self):
        self.base_url = settings.SERVICE_DISCOVERY_URL
        self.service_name = "data_storage_service"

    @handle_exceptions
    async def check_service_registration(self) -> bool:
        """
        Checks if the service is registered in Service Discovery.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url=f"{self.base_url}/services/",
                )
                response.raise_for_status()
                services = response.json()
                
                for service in services:
                    if service.get("name") == self.service_name:
                        return True
                return False
            
            except httpx.HTTPError as e:
                 raise HTTPException(
                   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   detail=f"Error communicating with Service Discovery: {e}"
                 ) from e

    @handle_exceptions
    async def register_service(self, address: str, port: int) -> None:
         """
        Registers the service in Service Discovery.
         """
         async with httpx.AsyncClient() as client:
              try:
                  response = await client.post(
                    url=f"{self.base_url}/services/register",
                     json = {
                         "name": self.service_name,
                         "address": address,
                         "port": port,
                         "metadata": {}
                     }
                 )
                  response.raise_for_status()

              except httpx.HTTPError as e:
                   raise HTTPException(
                      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                      detail=f"Error registering service in Service Discovery: {e}"
                  ) from e

    @handle_exceptions
    async def unregister_service(self) -> None:
        """
        Unregisters the service in Service Discovery.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url=f"{self.base_url}/services/",
                )
                response.raise_for_status()
                services = response.json()
                
                service_id_to_delete = None
                for service in services:
                    if service.get("name") == self.service_name:
                        service_id_to_delete = service.get("service_id")
                        break
                if service_id_to_delete:
                     response = await client.delete(
                         url=f"{self.base_url}/services/{service_id_to_delete}",
                    )
                     response.raise_for_status()
            
            except httpx.HTTPError as e:
               raise HTTPException(
                   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   detail=f"Error unregistering service in Service Discovery: {e}"
                ) from e