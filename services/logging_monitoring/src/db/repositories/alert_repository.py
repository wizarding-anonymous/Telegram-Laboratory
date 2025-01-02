from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Alert
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class AlertRepository:
    """
    Repository for performing CRUD operations on the Alert model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(
        self,
        metric: str,
        threshold: float,
        operator: str,
        notification_channel: str,
        email: Optional[str] = None,
        slack_webhook: Optional[str] = None,
    ) -> Alert:
        """
        Creates a new alert rule in the database.
        """
        logger.info(f"Creating alert rule for metric: {metric}")
        try:
            alert = Alert(
                metric=metric,
                threshold=threshold,
                operator=operator,
                notification_channel=notification_channel,
                email=email,
                slack_webhook=slack_webhook
            )
            self.session.add(alert)
            await self.session.commit()
            await self.session.refresh(alert)
            logger.info(f"Alert rule with id: {alert.id} created successfully")
            return alert
        except Exception as e:
            logger.error(f"Failed to create alert rule: {e}")
            raise DatabaseException(f"Failed to create alert rule: {e}") from e

    @handle_exceptions
    async def get(self, alert_id: int) -> Optional[Alert]:
        """
        Retrieves an alert rule by its ID.
        """
        logger.info(f"Getting alert rule with ID: {alert_id}")
        try:
            query = select(Alert).where(Alert.id == alert_id)
            result = await self.session.execute(query)
            alert = result.scalar_one_or_none()
            if alert:
                logger.debug(f"Alert rule with ID {alert_id} found.")
            else:
                 logger.warning(f"Alert rule with ID {alert_id} not found.")
            return alert
        except Exception as e:
             logger.error(f"Error getting alert rule with ID {alert_id}: {e}")
             raise DatabaseException(f"Failed to get alert rule with id {alert_id}: {e}") from e

    @handle_exceptions
    async def get_all(self) -> List[Alert]:
        """
        Retrieves all alert rules.
        """
        logger.info("Getting all alert rules")
        try:
            query = select(Alert)
            result = await self.session.execute(query)
            alerts = list(result.scalars().all())
            logger.debug(f"Found {len(alerts)} alert rules.")
            return alerts
        except Exception as e:
            logger.error(f"Error getting all alert rules: {e}")
            raise DatabaseException(f"Failed to get all alert rules: {e}") from e

    @handle_exceptions
    async def update(
        self,
        alert_id: int,
        metric: Optional[str] = None,
        threshold: Optional[float] = None,
        operator: Optional[str] = None,
        notification_channel: Optional[str] = None,
        email: Optional[str] = None,
        slack_webhook: Optional[str] = None,
    ) -> Optional[Alert]:
        """
        Updates an existing alert rule by its ID.
        """
        logger.info(f"Updating alert rule with ID: {alert_id}")
        try:
            query = select(Alert).where(Alert.id == alert_id)
            result = await self.session.execute(query)
            alert = result.scalar_one_or_none()
            if alert:
                if metric is not None:
                    alert.metric = metric
                if threshold is not None:
                     alert.threshold = threshold
                if operator is not None:
                     alert.operator = operator
                if notification_channel is not None:
                    alert.notification_channel = notification_channel
                if email is not None:
                    alert.email = email
                if slack_webhook is not None:
                     alert.slack_webhook = slack_webhook
                await self.session.commit()
                await self.session.refresh(alert)
                logger.info(f"Alert rule with id {alert_id} updated successfully.")
            else:
                 logger.warning(f"Alert rule with ID {alert_id} not found for update")
            return alert
        except Exception as e:
             logger.error(f"Error updating alert rule with ID: {alert_id}: {e}")
             raise DatabaseException(f"Failed to update alert rule with id {alert_id}: {e}") from e

    @handle_exceptions
    async def delete(self, alert_id: int) -> Optional[Alert]:
        """
        Deletes an alert rule by its ID.
        """
        logger.info(f"Deleting alert rule with ID: {alert_id}")
        try:
            query = delete(Alert).where(Alert.id == alert_id)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Alert rule with ID {alert_id} deleted successfully.")
            return result.scalar_one_or_none()
        except Exception as e:
             logger.error(f"Error deleting alert rule with ID: {alert_id}: {e}")
             raise DatabaseException(f"Failed to delete alert rule with id {alert_id}: {e}") from e