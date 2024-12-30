import factory
from factory.alchemy import SQLAlchemyModelFactory
from src.db.models import Block, Bot, Connection
from src.db.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from src.config import settings

class BaseFactory(SQLAlchemyModelFactory):
    """Base factory for SQLAlchemy models."""

    class Meta:
        abstract = True
        sqlalchemy_session_factory = get_session

class BlockFactory(BaseFactory):
    """Factory for creating Block model instances."""

    class Meta:
        model = Block

    id = factory.Sequence(lambda n: n)
    bot_id = 1
    type = "text_message"
    content = {"text": "Test Message"}
    connections = []

class BotFactory(BaseFactory):
    """Factory for creating Bot model instances."""

    class Meta:
        model = Bot

    id = factory.Sequence(lambda n: n)
    user_id = 1
    name = "Test Bot"
    description = "Test Description"
    status = "draft"
    version = "1.0.0"
    logic = {"start_block_id": 1}
    token = "test_token"
    library = "telegram_api"

class ConnectionFactory(BaseFactory):
    """Factory for creating Connection model instances."""
    
    class Meta:
        model = Connection
    
    id = factory.Sequence(lambda n: n)
    source_block_id = 1
    target_block_id = 2
    type = "default"