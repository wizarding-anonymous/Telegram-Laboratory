# services\data_storage_service\src\db\models\bot_model.py
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        func, text)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from .base import Base


class Bot(Base):
    """
    Модель данных для ботов в мета-базе данных.
    """

    __tablename__ = "bots"  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор бота
    user_id = Column(
        Integer, nullable=False, index=True, comment="ID пользователя, владеющего ботом"
    )
    name = Column(String(255), nullable=False, comment="Имя бота")
    description = Column(Text, nullable=True, comment="Описание бота")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата и время создания бота",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Дата и время последнего обновления бота",
    )

    # Связи с другими моделями
    blocks = relationship(
        "Block", back_populates="bot", cascade="all, delete-orphan"
    )  # Связь с блоками логики бота
    bot_metadata = relationship(
        "Metadata", back_populates="bot", cascade="all, delete-orphan"
    )  # Изменено с metadata на bot_metadata

    def __repr__(self):
        return f"<Bot(id={self.id}, user_id={self.user_id}, name={self.name})>"

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
            # Используем запрос к базе данных для проверки состояния миграций
            # Например, можно проверить текущую версию базы данных с помощью Alembic
            result = await session.execute(
                text("SELECT version_num FROM alembic_version")
            )
            version = result.scalar()

            if version:
                # Проверяем, если версия схемы базы данных актуальна
                if version == "your_expected_version":  # Замените на вашу версию схемы
                    return "healthy"
                else:
                    return "pending"
            else:
                return "pending"
        except Exception as e:
            # Если возникает ошибка при проверке миграций
            return f"Error checking migrations: {str(e)}"
