from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException, status
from loguru import logger

from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class ElasticsearchClient:
    """
    Client for interacting with Elasticsearch.
    """

    def __init__(self):
        self.base_url = settings.ELASTICSEARCH_URL  # Corrected variable name

    @handle_exceptions
    async def send_log(self, log_data: Dict[str, Any]) -> None:
        """
        Sends a log entry to Elasticsearch.
        """
        logging_client.debug(f"Sending log to Elasticsearch: {log_data}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=f"{self.base_url}/_doc",
                    json=log_data,
                     timeout=10
                )
                response.raise_for_status()
                logging_client.debug(f"Log sent to Elasticsearch successfully. Response: {response.text}")
        except httpx.HTTPError as e:
            logging_client.error(f"Error sending log to Elasticsearch: {e}")
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error sending log to Elasticsearch: {e}"
                ) from e
        except Exception as e:
             logging_client.error(f"An unexpected error occurred: {e}")
             raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Unexpected error: {e}"
                    ) from e

    @handle_exceptions
    async def check_connection(self) -> bool:
        """
        Check connection to Elasticsearch
        """
        logging_client.debug("Checking connection to Elasticsearch.")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=f"{self.base_url}",
                    timeout=10
                )
                response.raise_for_status()
                logging_client.debug("Connection to Elasticsearch is healthy.")
                return True
        except httpx.HTTPError as e:
            logging_client.error(f"Connection to Elasticsearch failed: {e}")
            return False
        except Exception as e:
             logging_client.error(f"An unexpected error occurred: {e}")
             return False