# services\api_gateway\src\db\database.py
from typing import Any, Dict, Optional, Type, TypeVar
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Column, DateTime, func
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)

# Определяем конвенции именования для PostgreSQL
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Создаем метаданные с нашими конвенциями
metadata = MetaData(naming_convention=convention)

# Создаем базовый класс для моделей
Base = declarative_base(metadata=metadata)

# Типизация для моделей
ModelType = TypeVar("ModelType", bound=Base)

class BaseModel(Base):
    """Базовый класс для всех моделей с общими полями и методами."""
    
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Создание объекта модели из словаря."""
        return cls(**{
            k: v for k, v in data.items() 
            if hasattr(cls, k) and not k.startswith('_')
        })

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация модели в словарь."""
        result = {}
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[key] = value
        return result

    def update(self, data: Dict[str, Any]) -> None:
        """Обновление полей модели из словаря."""
        for key, value in data.items():
            if hasattr(self, key) and not key.startswith('_'):
                setattr(self, key, value)

class Database:
    """Класс для управления подключением к базе данных."""
    
    def __init__(self) -> None:
        """Инициализация подключения к базе данных."""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def init(self) -> None:
        """Инициализация подключения к базе данных."""
        if not self._engine:
            try:
                # Создаем движок SQLAlchemy
                self._engine = create_async_engine(
                    settings.DATABASE_URL,
                    echo=settings.DB_ECHO_LOG,
                    pool_size=settings.DB_POOL_SIZE,
                    max_overflow=settings.DB_MAX_OVERFLOW,
                    pool_timeout=settings.DB_POOL_TIMEOUT,
                    pool_recycle=settings.DB_POOL_RECYCLE,
                    pool_pre_ping=True
                )

                # Создаем фабрику сессий
                self._session_factory = async_sessionmaker(
                    bind=self._engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=False
                )

                logger.info("Database connection initialized successfully")

            except Exception as e:
                logger.error(f"Error initializing database: {e}")
                raise

    async def dispose(self) -> None:
        """Закрытие соединения с базой данных."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database connection closed")

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """
        Контекстный менеджер для работы с сессией базы данных.
        
        Yields:
            AsyncSession: Сессия SQLAlchemy
        """
        if not self._session_factory:
            await self.init()
            
        session: AsyncSession = self._session_factory()  # type: ignore
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

class BaseRepository:
    """Базовый класс для репозиториев."""

    def __init__(self, model: Type[ModelType], db: Database) -> None:
        """
        Инициализация репозитория.

        Args:
            model: Класс модели SQLAlchemy
            db: Экземпляр класса Database
        """
        self.model = model
        self.db = db

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Создание новой записи.

        Args:
            data: Данные для создания записи

        Returns:
            ModelType: Созданная запись
        """
        async with self.db.session() as session:
            instance = self.model.from_dict(data)
            session.add(instance)
            await session.flush()
            return instance

    async def get(self, id: Any) -> Optional[ModelType]:
        """
        Получение записи по id.

        Args:
            id: Идентификатор записи

        Returns:
            Optional[ModelType]: Найденная запись или None
        """
        async with self.db.session() as session:
            query = select(self.model).where(self.model.id == id)
            result = await session.execute(query)
            return result.scalars().first()

    async def get_by_field(
        self,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """
        Получение записи по значению поля.

        Args:
            field: Имя поля
            value: Значение поля

        Returns:
            Optional[ModelType]: Найденная запись или None
        """
        async with self.db.session() as session:
            query = select(self.model).where(getattr(self.model, field) == value)
            result = await session.execute(query)
            return result.scalars().first()

    async def list(self, query: Optional[Select] = None) -> list[ModelType]:
        """
        Получение списка записей.

        Args:
            query: Опциональный SQLAlchemy запрос

        Returns:
            list[ModelType]: Список записей
        """
        async with self.db.session() as session:
            if query is None:
                query = select(self.model)
            result = await session.execute(query)
            return list(result.scalars().all())

    async def update(
        self,
        id: Any,
        data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Обновление записи.

        Args:
            id: Идентификатор записи
            data: Данные для обновления

        Returns:
            Optional[ModelType]: Обновленная запись или None
        """
        async with self.db.session() as session:
            instance = await self.get(id)
            if instance:
                instance.update(data)
                session.add(instance)
                await session.flush()
                return instance
            return None

    async def delete(self, id: Any) -> bool:
        """
        Удаление записи.

        Args:
            id: Идентификатор записи

        Returns:
            bool: True если запись удалена, False если запись не найдена
        """
        async with self.db.session() as session:
            instance = await self.get(id)
            if instance:
                await session.delete(instance)
                return True
            return False

# Создание синглтона для использования в приложении
_database: Optional[Database] = None

def get_database() -> Database:
    """
    Получение экземпляра Database.
    
    Returns:
        Database instance
    """
    global _database
    
    if _database is None:
        _database = Database()
    
    return _database