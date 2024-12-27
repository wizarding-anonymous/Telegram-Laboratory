# user_dashboard/src/core/bot_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from user_dashboard.src.models.bot_model import Bot
from user_dashboard.src.schemas.bot_schema import BotCreate, BotUpdate

async def get_user_bots(db: AsyncSession, user_id: int) -> list[Bot]:
    result = await db.execute(select(Bot).where(Bot.owner_id == user_id))
    bots = result.scalars().all()
    return bots

async def create_bot(db: AsyncSession, user_id: int, bot_create: BotCreate) -> Bot:
    new_bot = Bot(
        name=bot_create.name,
        description=bot_create.description,
        owner_id=user_id
    )
    db.add(new_bot)
    await db.commit()
    await db.refresh(new_bot)
    return new_bot

async def update_bot(db: AsyncSession, user_id: int, bot_id: int, bot_update: BotUpdate) -> bool:
    result = await db.execute(select(Bot).where(Bot.id == bot_id, Bot.owner_id == user_id))
    bot = result.scalars().first()
    if not bot:
        return False
    
    if bot_update.name:
        bot.name = bot_update.name
    if bot_update.description:
        bot.description = bot_update.description
    
    db.add(bot)
    await db.commit()
    return True

async def delete_bot(db: AsyncSession, user_id: int, bot_id: int) -> bool:
    result = await db.execute(select(Bot).where(Bot.id == bot_id, Bot.owner_id == user_id))
    bot = result.scalars().first()
    if not bot:
        return False
    
    await db.delete(bot)
    await db.commit()
    return True
