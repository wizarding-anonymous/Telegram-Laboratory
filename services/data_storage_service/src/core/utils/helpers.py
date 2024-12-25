# services\data_storage_service\src\core\utils\helpers.py
# src/core/utils/helpers.py
import random
import string
from datetime import datetime
from functools import wraps

from fastapi import HTTPException
from loguru import logger


class MigrationException(Exception):
    """Ошибка, связанная с миграцией базы данных."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DatabaseException(Exception):
    """Ошибка, связанная с базой данных."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def handle_exceptions(func):
    """
    Декоратор для обработки исключений в асинхронных функциях.

    Этот декоратор перехватывает исключения, возникающие в процессе выполнения функции,
    логирует их и возвращает структурированный ответ с ошибкой.

    Args:
        func (function): Асинхронная функция, к которой применяется декоратор.

    Returns:
        function: Декорированная функция с обработкой исключений.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as exc:
            logger.error(f"HTTPException: {exc.detail}")
            raise exc  # Перехватываем и пробрасываем исключение
        except MigrationException as exc:
            logger.error(f"MigrationException: {exc.message}")
            raise HTTPException(
                status_code=500,
                detail=f"Migration error: {exc.message}",
            )
        except DatabaseException as exc:
            logger.error(f"DatabaseException: {exc.message}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {exc.message}",
            )
        except Exception as exc:
            logger.exception("Unhandled exception")
            # Обрабатываем все остальные ошибки
            raise HTTPException(
                status_code=500,
                detail="An internal server error occurred. Please try again later.",
            ) from exc

    return wrapper


def generate_random_string(length: int = 16) -> str:
    """
    Генерация случайной строки заданной длины.

    Используется для создания уникальных идентификаторов или ключей.

    Args:
        length (int): Длина генерируемой строки.

    Returns:
        str: Случайная строка.
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def format_datetime(dt: datetime) -> str:
    """
    Форматирование даты и времени в строку.

    Преобразует объект datetime в строку формата 'YYYY-MM-DD HH:MM:SS'.

    Args:
        dt (datetime): Дата и время для форматирования.

    Returns:
        str: Строковое представление даты и времени.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_datetime(dt_str: str) -> datetime:
    """
    Преобразование строки в объект datetime.

    Преобразует строковое представление даты и времени в объект datetime.

    Args:
        dt_str (str): Строка даты и времени в формате 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        datetime: Объект datetime.
    """
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Invalid datetime format: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Expected 'YYYY-MM-DD HH:MM:SS'",
        )


def convert_to_utc(dt: datetime) -> datetime:
    """
    Преобразование времени в UTC.

    Конвертирует время в объект datetime в формате UTC.

    Args:
        dt (datetime): Дата и время.

    Returns:
        datetime: Время в формате UTC.
    """
    return dt.astimezone(datetime.timezone.utc)


def check_permission(permission: str) -> bool:
    """
    Проверка наличия разрешения для выполнения операции.

    Проверяет, есть ли у пользователя необходимое разрешение.

    Args:
        permission (str): Название разрешения.

    Returns:
        bool: True, если разрешение присутствует, иначе False.
    """
    valid_permissions = ["create_bot", "update_bot", "delete_bot", "view_bot"]
    if permission not in valid_permissions:
        logger.warning(f"Invalid permission: {permission}")
        return False
    return True


# Дополнительные утилиты для миграций


async def check_migrations_status(bot_id: int) -> str:
    """
    Проверка состояния миграций для базы данных бота.

    Возвращает строку с состоянием миграций (например, "healthy" или "pending").

    Args:
        bot_id (int): ID бота для проверки миграций.

    Returns:
        str: Статус состояния миграций.
    """
    # Это всего лишь пример. Реальная логика должна проверять наличие примененных миграций.
    # Например, через Alembic или через систему версий миграций базы данных.
    migrations_pending = (
        False  # Предположим, что миграции могут быть в состоянии ожидания.
    )

    if migrations_pending:
        raise MigrationException(f"Migrations are pending for bot {bot_id}.")
    else:
        return "healthy"  # Миграции применены успешно
