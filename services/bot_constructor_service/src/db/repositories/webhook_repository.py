from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.models.webhook_model import Webhook
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class WebhookRepository:
    """
    Repository for performing database operations on webhook entities.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the WebhookRepository with a database session."""
        self.session = session
        logging_client.info("WebhookRepository initialized")

    @handle_exceptions
    async def create(self, webhook_data: dict) -> Webhook:
        """Creates a new webhook in the database."""
        logging_client.info(f"Creating new webhook with data: {webhook_data}")
        webhook = Webhook(**webhook_data)
        self.session.add(webhook)
        await self.session.commit()
        await self.session.refresh(webhook)
        logging_client.info(f"Webhook with id: {webhook.id} created successfully")
        return webhook

    @handle_exceptions
    async def get_by_id(self, webhook_id: int) -> Optional[Webhook]:
        """Retrieves a webhook by its ID."""
        logging_client.info(f"Getting webhook by id: {webhook_id}")
        webhook = await self.session.get(Webhook, webhook_id)
        if webhook:
           logging_client.info(f"Webhook with id: {webhook_id} retrieved successfully")
        else:
            logging_client.warning(f"Webhook with id: {webhook_id} not found")
        return webhook

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[Webhook]:
        """Retrieves all webhooks for a specific bot."""
        logging_client.info(f"Getting all webhooks for bot_id: {bot_id}")
        query = select(Webhook).where(Webhook.bot_id == bot_id)
        result = await self.session.execute(query)
        webhooks = result.scalars().all()
        logging_client.info(f"Found {len(webhooks)} webhooks for bot_id: {bot_id}")
        return list(webhooks)

    @handle_exceptions
    async def update(self, webhook_id: int, webhook_data: dict) -> Optional[Webhook]:
        """Updates an existing webhook."""
        logging_client.info(f"Updating webhook with id: {webhook_id} with data: {webhook_data}")
        webhook = await self.session.get(Webhook, webhook_id)
        if webhook:
            for key, value in webhook_data.items():
                setattr(webhook, key, value)
            await self.session.commit()
            await self.session.refresh(webhook)
            logging_client.info(f"Webhook with id: {webhook_id} updated successfully")
            return webhook
        logging_client.warning(f"Webhook with id: {webhook_id} not found for update")
        return None

    @handle_exceptions
    async def delete(self, webhook_id: int) -> bool:
        """Deletes a webhook by its ID."""
        logging_client.info(f"Deleting webhook with id: {webhook_id}")
        webhook = await self.session.get(Webhook, webhook_id)
        if webhook:
            await self.session.delete(webhook)
            await self.session.commit()
            logging_client.info(f"Webhook with id: {webhook_id} deleted successfully")
            return True
        logging_client.warning(f"Webhook with id: {webhook_id} not found for delete")
        return False