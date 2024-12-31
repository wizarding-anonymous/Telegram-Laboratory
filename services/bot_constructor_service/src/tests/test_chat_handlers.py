import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import chat_handlers
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
    mock.get_chat_members.return_value = {"ok": True, "result": []}
    mock.ban_chat_member.return_value = {"ok": True}
    mock.unban_chat_member.return_value = {"ok": True}
    mock.set_chat_title.return_value = {"ok": True}
    mock.set_chat_description.return_value = {"ok": True}
    mock.pin_chat_message.return_value = {"ok": True}
    mock.unpin_chat_message.return_value = {"ok": True}
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


@pytest.mark.asyncio
async def test_get_chat_members_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful getting chat members.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    result = await chat_handlers.get_chat_members(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.get_chat_members.assert_called_once_with(chat_id=chat_id)

@pytest.mark.asyncio
async def test_get_chat_members_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test getting chat members with not found block.
    """
    block_id = 999
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await chat_handlers.get_chat_members(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.get_chat_members.assert_not_called()


@pytest.mark.asyncio
async def test_ban_user_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful ban of user.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id}
    result = await chat_handlers.ban_user(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.ban_chat_member.assert_called_once_with(
      chat_id=chat_id, user_id=user_id
    )


@pytest.mark.asyncio
async def test_ban_user_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test ban user with not found block.
    """
    block_id = 999
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
      await chat_handlers.ban_user(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.ban_chat_member.assert_not_called()



@pytest.mark.asyncio
async def test_unban_user_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful unban of user.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id}
    result = await chat_handlers.unban_user(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.unban_chat_member.assert_called_once_with(
        chat_id=chat_id, user_id=user_id
    )

@pytest.mark.asyncio
async def test_unban_user_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test unban user with not found block.
    """
    block_id = 999
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
      await chat_handlers.unban_user(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.unban_chat_member.assert_not_called()

@pytest.mark.asyncio
async def test_set_chat_title_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful set chat title.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    title = "New Title"
    test_data = {"block_id": block_id, "chat_id": chat_id, "title": title}
    result = await chat_handlers.set_chat_title(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.set_chat_title.assert_called_once_with(
        chat_id=chat_id, title=title
    )

@pytest.mark.asyncio
async def test_set_chat_title_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test set chat title with not found block.
    """
    block_id = 999
    chat_id = 123
    title = "New Title"
    test_data = {"block_id": block_id, "chat_id": chat_id, "title": title}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await chat_handlers.set_chat_title(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.set_chat_title.assert_not_called()


@pytest.mark.asyncio
async def test_set_chat_description_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful set chat description.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    description = "New Description"
    test_data = {"block_id": block_id, "chat_id": chat_id, "description": description}
    result = await chat_handlers.set_chat_description(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.set_chat_description.assert_called_once_with(
        chat_id=chat_id, description=description
    )

@pytest.mark.asyncio
async def test_set_chat_description_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test set chat description with not found block.
    """
    block_id = 999
    chat_id = 123
    description = "New Description"
    test_data = {"block_id": block_id, "chat_id": chat_id, "description": description}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await chat_handlers.set_chat_description(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.set_chat_description.assert_not_called()

@pytest.mark.asyncio
async def test_pin_chat_message_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful pin chat message.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    message_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "message_id": message_id}
    result = await chat_handlers.pin_message(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.pin_chat_message.assert_called_once_with(
        chat_id=chat_id, message_id=message_id
    )

@pytest.mark.asyncio
async def test_pin_chat_message_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test pin chat message with not found block.
    """
    block_id = 999
    chat_id = 123
    message_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "message_id": message_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await chat_handlers.pin_message(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.pin_chat_message.assert_not_called()


@pytest.mark.asyncio
async def test_unpin_chat_message_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful unpin chat message.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    message_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "message_id": message_id}
    result = await chat_handlers.unpin_message(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.unpin_chat_message.assert_called_once_with(
        chat_id=chat_id, message_id=message_id
    )

@pytest.mark.asyncio
async def test_unpin_chat_message_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test unpin chat message with not found block.
    """
    block_id = 999
    chat_id = 123
    message_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "message_id": message_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await chat_handlers.unpin_message(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.unpin_chat_message.assert_not_called()