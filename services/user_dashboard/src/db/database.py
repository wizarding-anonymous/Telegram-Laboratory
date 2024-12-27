# user_dashboard/src/db/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Создание базы для моделей
Base = declarative_base()

# Создание асинхронного движка для базы данных
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,  # Включает/отключает логирование SQL-запросов
    future=True,  # Использование новой версии SQLAlchemy API
)

# Создание асинхронной фабрики сессий
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Сессия сохраняет данные после commit
)

# Функция для получения сессии
async def get_db():
    """
    Получает сессию базы данных.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Инициализация базы данных
async def init_db():
    """
    Инициализирует базу данных, выполняя миграции и создавая схемы.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
