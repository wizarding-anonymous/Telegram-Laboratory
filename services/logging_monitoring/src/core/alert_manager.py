from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session
from src.db.repositories import AlertRepository
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AlertManager:
    """
    Manages alert rules in the Logging and Monitoring service.
    """

    def __init__(self, alert_repository: AlertRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.repository = alert_repository
        self.session = session

    @handle_exceptions
    async def create_alert(
        self,
        metric: str,
        threshold: float,
        operator: str,
        notification_channel: str,
        email: Optional[str] = None,
        slack_webhook: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new alert rule."""
        logging_client.info(f"Creating alert rule for metric: {metric}, threshold: {threshold}, operator: {operator}")
        try:
            alert = await self.repository.create(
                metric=metric,
                threshold=threshold,
                operator=operator,
                notification_channel=notification_channel,
                email=email,
                slack_webhook=slack_webhook
            )
            logging_client.info(f"Alert rule created successfully with ID: {alert.id}")
            return alert.__dict__
        except Exception as e:
             logging_client.error(f"Error creating alert rule: {e}")
             raise

    @handle_exceptions
    async def get_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves an alert rule by its ID."""
        logging_client.info(f"Getting alert rule with ID: {alert_id}")
        try:
            alert = await self.repository.get(alert_id=alert_id)
            if not alert:
               logging_client.warning(f"Alert rule with ID {alert_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
                )
            logging_client.info(f"Alert rule with ID {alert_id} retrieved successfully.")
            return alert.__dict__
        except Exception as e:
             logging_client.error(f"Error getting alert rule with ID {alert_id}: {e}")
             raise

    @handle_exceptions
    async def get_all_alerts(self) -> List[Dict[str, Any]]:
        """Retrieves all alert rules."""
        logging_client.info("Getting all alert rules.")
        try:
            alerts = await self.repository.get_all()
            logging_client.info(f"Successfully retrieved {len(alerts)} alert rules")
            return [alert.__dict__ for alert in alerts]
        except Exception as e:
            logging_client.error(f"Error getting all alert rules: {e}")
            raise

    @handle_exceptions
    async def update_alert(
        self,
        alert_id: int,
        metric: Optional[str] = None,
        threshold: Optional[float] = None,
        operator: Optional[str] = None,
        notification_channel: Optional[str] = None,
        email: Optional[str] = None,
        slack_webhook: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing alert rule."""
        logging_client.info(f"Updating alert rule with ID: {alert_id}")
        try:
            alert = await self.repository.update(
                alert_id=alert_id,
                metric=metric,
                threshold=threshold,
                operator=operator,
                notification_channel=notification_channel,
                email=email,
                slack_webhook=slack_webhook
            )
            if not alert:
                 logging_client.warning(f"Alert rule with ID {alert_id} not found for update.")
                 raise HTTPException(
                     status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
                 )
            logging_client.info(f"Alert rule with ID {alert_id} updated successfully.")
            return alert.__dict__
        except Exception as e:
             logging_client.error(f"Error updating alert with ID {alert_id}: {e}")
             raise

    @handle_exceptions
    async def delete_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Deletes an alert rule by its ID."""
        logging_client.info(f"Deleting alert rule with ID: {alert_id}")
        try:
            alert = await self.repository.delete(alert_id=alert_id)
            if not alert:
               logging_client.warning(f"Alert rule with ID {alert_id} not found for deletion.")
               raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
                )
            logging_client.info(f"Alert rule with ID {alert_id} deleted successfully.")
            return alert.__dict__
        except Exception as e:
            logging_client.error(f"Error deleting alert rule with ID {alert_id}: {e}")
            raise