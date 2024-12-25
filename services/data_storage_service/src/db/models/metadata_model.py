# services\data_storage_service\src\db\models\metadata_model.py
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        func, text)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from .base import Base


class Metadata(Base):
    """
    Модель данных для метаданных бота в мета-базе данных.
    """

    __tablename__ = "metadata"  # Название таблицы в базе данных

    id = Column(
        Integer, primary_key=True, index=True
    )  # Уникальный идентификатор метаданных
    bot_id = Column(
        Integer,
        ForeignKey("bots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID бота, к которому относятся метаданные",
    )
    metadata_key = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Ключ метаданных (например, 'version', 'description')",
    )
    metadata_value = Column(
        Text,
        nullable=False,
        comment="Значение метаданных (например, '1.0', 'My awesome bot')",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата и время создания метаданных",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Дата и время последнего обновления метаданных",
    )

    # Связь с таблицей ботов (обновлено для соответствия с изменениями в модели Bot)
    bot = relationship(
        "Bot", back_populates="bot_metadata"
    )  # Изменено с metadata на bot_metadata

    def __repr__(self):
        return f"<Metadata(id={self.id}, bot_id={self.bot_id}, metadata_key={self.metadata_key})>"

    @classmethod
    async def check_migrations_status(cls, session: AsyncSession):
        """
        Проверка состояния миграций для базы данных бота.
        Это можно сделать через проверку версии схемы базы данных или другой логики.

        Возвращает:
            - "healthy" если миграции применены
            - "pending" если миграции не были применены
        """
        try:
            # Выполним запрос к базе данных, чтобы проверить текущую версию миграций
            result = await session.execute(
                text("SELECT version_num FROM alembic_version")
            )
            version = result.scalar()

            if version:
                # Проверка, если версия миграций актуальна
                if (
                    version == "your_expected_version"
                ):  # Замените на вашу ожидаемую версию
                    return "healthy"
                else:
                    return "pending"
            else:
                return "pending"  # Если версия не найдена, миграции не применены

        except Exception as e:
            # В случае ошибки при проверке состояния миграций
            return f"Error checking migrations: {str(e)}"
