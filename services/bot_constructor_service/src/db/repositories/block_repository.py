# src/db/repositories/block_repository.py

from sqlalchemy.ext.asyncio import AsyncSession  # Импортируем AsyncSession для асинхронной работы с базой данных
from sqlalchemy.future import select
from sqlalchemy import update, delete
from src.db.models.block_model import Block  # Импортируем модель Block
from typing import Optional

class BlockRepository:
    """
    Репозиторий для управления операциями с таблицей Block в базе данных.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория с сессией базы данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.session = session

    async def get_by_id(self, block_id: int) -> Optional[Block]:
        """
        Получить блок по его ID.

        Args:
            block_id (int): ID блока.

        Returns:
            Block | None: Возвращает блок, если найден, иначе None.
        """
        query = select(Block).where(Block.id == block_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_bot(self, bot_id: int, skip: int = 0, limit: int = 100) -> list[Block]:
        """
        Получить все блоки для конкретного бота с пагинацией.

        Args:
            bot_id (int): ID бота.
            skip (int): Количество записей для пропуска.
            limit (int): Максимальное количество записей для извлечения.

        Returns:
            list[Block]: Список блоков.
        """
        query = select(Block).where(Block.bot_id == bot_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, block_data: dict) -> Block:
        """
        Создать новый блок.

        Args:
            block_data (dict): Данные для нового блока.

        Returns:
            Block: Созданный блок.
        """
        block = Block(**block_data)
        self.session.add(block)
        await self.session.flush()  # Flush для того, чтобы блок получил ID перед коммитом.
        await self.session.commit()
        return block

    async def update(self, block_id: int, block_data: dict) -> Optional[Block]:
        """
        Обновить существующий блок.

        Args:
            block_id (int): ID блока для обновления.
            block_data (dict): Данные для обновления.

        Returns:
            Block | None: Обновленный блок, если найден, иначе None.
        """
        query = update(Block).where(Block.id == block_id).values(**block_data).returning(Block)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, block_id: int) -> bool:
        """
        Удалить блок по его ID.

        Args:
            block_id (int): ID блока для удаления.

        Returns:
            bool: True, если блок был удален, иначе False.
        """
        query = delete(Block).where(Block.id == block_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
