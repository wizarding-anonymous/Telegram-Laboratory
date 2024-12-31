import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import webhook_handlers
from src.integrations.telegram import TelegramAPI
from src.core.utils.exceptions import ObjectNotFoundException
from typing import Dict, Any
from src.db import get_session
from sqlalchemy import text


@pytest.fixture
def mock_telegram_api() -> AsyncMock:
    """
    Fixture to create a mock TelegramAPI client.
    """
    mock = AsyncMock(spec=TelegramAPI)
    mock.set_webhook.return_value = {"ok": True}
    mock.delete_webhook.return_value = {"ok": True}
    return mock


@pytest.fixture
async def create_test_bot() -> Dict[str, Any]:
    """
    Fixture to create a test bot in the database.
    """
    async with get_session() as session:
        query = text(
            """
            INSERT INTO bots (user_id, name)
            VALUES (:user_id, :name)
            RETURNING id, user_id, name, created_at;
        """
        )
        params = {"user_id": 1, "name": "Test Bot"}
        result = await session.execute(query, params)
        await session.commit()
        bot = result.fetchone()
        return dict(bot._mapping)


@pytest.fixture
async def create_test_block(create_test_bot) -> Dict[str, Any]:
    """
    Fixture to create a test block in the database.
    """
    bot_id = create_test_bot["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO blocks (bot_id, type, content)
            VALUES (:bot_id, :type, :content)
            RETURNING id, bot_id, type, content, created_at;
        """
        )
        params = {"bot_id": bot_id, "type": "message", "content": {"text": "Test message"}}
        result = await session.execute(query, params)
        await session.commit()
        block = result.fetchone()
        return dict(block._mapping)

@pytest.fixture
async def create_test_webhook(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test webhook in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
         query = text(
            """
            INSERT INTO webhooks (block_id, url)
            VALUES (:block_id, :url)
            RETURNING id, block_id, url, created_at;
            """
        )
         params = {"block_id": block_id, "url": "test_url"}
         result = await session.execute(query, params)
         await session.commit()
         webhook = result.fetchone()
         return dict(webhook._mapping)

@pytest.mark.asyncio
async def test_set_webhook_success(
    mock_telegram_api: AsyncMock,
    create_test_webhook: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful setting webhook.
    """
    webhook_id = create_test_webhook["id"]
    block_id = create_test_block["id"]
    test_data = {"block_id": block_id}
    
    result = await webhook_handlers.set_webhook(
        mock_telegram_api, test_data
    )
    assert result is not None
    mock_telegram_api.set_webhook.assert_called_once()
    mock_telegram_api.set_webhook.assert_called_with(url="test_url")
    
@pytest.mark.asyncio
async def test_set_webhook_not_found_block(
    mock_telegram_api: AsyncMock,
):
    """
    Test set webhook with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await webhook_handlers.set_webhook(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Webhook not found"
    mock_telegram_api.set_webhook.assert_not_called()
    

@pytest.mark.asyncio
async def test_delete_webhook_success(
    mock_telegram_api: AsyncMock,
    create_test_webhook: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful deleting webhook.
    """
    webhook_id = create_test_webhook["id"]
    block_id = create_test_block["id"]
    test_data = {"block_id": block_id}
    
    result = await webhook_handlers.delete_webhook(
        mock_telegram_api, test_data
    )
    assert result is not None
    mock_telegram_api.delete_webhook.assert_called_once()

@pytest.mark.asyncio
async def test_delete_webhook_not_found_block(
    mock_telegram_api: AsyncMock,
):
    """
    Test delete webhook with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await webhook_handlers.delete_webhook(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Webhook not found"
    mock_telegram_api.delete_webhook.assert_not_called()