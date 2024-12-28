from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from dotenv import load_dotenv
from src.db.models import Base  # Импортируйте модели
from src.config import settings

# Загружаем переменные окружения из .env файла
load_dotenv()

# Alembic Config объект, который предоставляет доступ к значениям в используемом .ini файле
config = context.config

# Получаем строку подключения к базе данных из переменной окружения
# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = settings.full_database_url

if DATABASE_URL:
    # Устанавливаем строку подключения в конфигурацию Alembic
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Конфигурация логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Мета-данные для поддержки автогенерации миграций
target_metadata = Base.metadata


def run_migrations_offline():
    """Запускаем миграции в оффлайн-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запускаем миграции в онлайн-режиме."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Включает сравнение типов столбцов для миграций
        )

        with context.begin_transaction():
            context.run_migrations()


# Выполняем миграции в зависимости от режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()