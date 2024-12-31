import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import media_group_handlers
from src.integrations.telegram import TelegramAPI
from src.core.utils.exceptions import ObjectNotFoundException
from typing import Dict, Any, List
from src.db import get_session
from sqlalchemy import text
from src.core.logic_manager.base import Block


@pytest.fixture
def mock_telegram_api() -> AsyncMock:
    """
    Fixture to create a mock TelegramAPI client.
    """
    mock = AsyncMock(spec=TelegramAPI)
    mock.send_media_group.return_value = {"ok": True}
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
async def create_test_media_group(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test media group block in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO media_groups (block_id, items)
            VALUES (:block_id, :items)
            RETURNING id, block_id, items, created_at;
            """
        )
        params = {
            "block_id": block_id,
            "items": [
                {"type": "photo", "media": "test_photo_url"},
                {"type": "video", "media": "test_video_url"},
            ],
        }
        result = await session.execute(query, params)
        await session.commit()
        media_group = result.fetchone()
        return dict(media_group._mapping)

@pytest.mark.asyncio
async def test_send_media_group_success(
    mock_telegram_api: AsyncMock,
    create_test_media_group: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful sending of a media group.
    """
    media_group_id = create_test_media_group["id"]
    block_id = create_test_block["id"]
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    
    result = await media_group_handlers.send_media_group(
        mock_telegram_api, test_data
    )
    assert result is not None
    mock_telegram_api.send_media_group.assert_called_once()
    mock_telegram_api.send_media_group.assert_called_with(
        chat_id=chat_id,
        media=[
            {"type": "photo", "media": "test_photo_url"},
            {"type": "video", "media": "test_video_url"},
        ],
    )


@pytest.mark.asyncio
async def test_send_media_group_not_found_block(
    mock_telegram_api: AsyncMock,
):
    """
    Test send media group with not found block.
    """
    block_id = 999
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await media_group_handlers.send_media_group(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Media group not found"
    mock_telegram_api.send_media_group.assert_not_called()