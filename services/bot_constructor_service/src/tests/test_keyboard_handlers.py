import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import keyboard_handlers
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
    mock.send_message.return_value = {"ok": True}
    mock.send_reply_keyboard.return_value = {"ok": True}
    mock.send_inline_keyboard.return_value = {"ok": True}
    mock.remove_keyboard.return_value = {"ok": True}
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
async def create_test_keyboard(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test keyboard in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
         query = text(
            """
            INSERT INTO keyboards (block_id, buttons, type)
            VALUES (:block_id, :buttons, :type)
            RETURNING id, block_id, buttons, type, created_at;
            """
        )
         params = {"block_id": block_id, "buttons": [{"text": "test"}], "type": "reply"}
         result = await session.execute(query, params)
         await session.commit()
         keyboard = result.fetchone()
         return dict(keyboard._mapping)


@pytest.mark.asyncio
async def test_create_reply_keyboard_success(
    mock_telegram_api: AsyncMock,
    create_test_keyboard: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of reply keyboard.
    """
    keyboard_id = create_test_keyboard["id"]
    block_id = create_test_block["id"]
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    
    result = await keyboard_handlers.create_reply_keyboard(
        mock_telegram_api, test_data
    )
    assert result is not None
    mock_telegram_api.send_reply_keyboard.assert_called_once()
    mock_telegram_api.send_reply_keyboard.assert_called_with(chat_id=chat_id, buttons=[{"text": "test"}])

@pytest.mark.asyncio
async def test_create_reply_keyboard_not_found_block(
    mock_telegram_api: AsyncMock,
):
    """
    Test create reply keyboard with not found block.
    """
    block_id = 999
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await keyboard_handlers.create_reply_keyboard(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Keyboard not found"
    mock_telegram_api.send_reply_keyboard.assert_not_called()

@pytest.mark.asyncio
async def test_create_inline_keyboard_success(
    mock_telegram_api: AsyncMock,
    create_test_keyboard: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful creation of inline keyboard.
    """
    keyboard_id = create_test_keyboard["id"]
    block_id = create_test_block["id"]
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    
    async with get_session() as session:
          query = text(
            """
            UPDATE keyboards
            SET type = :type
            WHERE id = :keyboard_id
            """
        )
          params = {
            "keyboard_id": keyboard_id,
            "type": "inline"
        }
          await session.execute(query, params)
          await session.commit()
          
    result = await keyboard_handlers.create_inline_keyboard(
        mock_telegram_api, test_data
    )
    assert result is not None
    mock_telegram_api.send_inline_keyboard.assert_called_once()
    mock_telegram_api.send_inline_keyboard.assert_called_with(chat_id=chat_id, buttons=[{"text": "test"}])

@pytest.mark.asyncio
async def test_create_inline_keyboard_not_found_block(
     mock_telegram_api: AsyncMock,
):
    """
     Test create inline keyboard with not found block.
    """
    block_id = 999
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
      await keyboard_handlers.create_inline_keyboard(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Keyboard not found"
    mock_telegram_api.send_inline_keyboard.assert_not_called()

@pytest.mark.asyncio
async def test_remove_keyboard_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful removal of keyboard.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    result = await keyboard_handlers.remove_keyboard(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.remove_keyboard.assert_called_once()
    mock_telegram_api.remove_keyboard.assert_called_with(chat_id=chat_id)
    
@pytest.mark.asyncio
async def test_remove_keyboard_not_found_block(
    mock_telegram_api: AsyncMock,
):
    """
    Test remove keyboard with not found block.
    """
    block_id = 999
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
      await keyboard_handlers.remove_keyboard(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.remove_keyboard.assert_not_called()