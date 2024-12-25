# services\data_storage_service\src\core\utils\validators.py
import string

from src.core.utils.helpers import MigrationException
from src.db.database import check_migrations_status


def validate_bot_name(name: str) -> str:
    """
    Проверка валидности имени бота.
    Имя не должно быть пустым, не должно содержать спецсимволов.

    Args:
        name (str): Имя бота.

    Returns:
        str: Валидированное имя бота.

    Raises:
        ValueError: Если имя бота пустое или содержит спецсимволы.
    """
    if not isinstance(name, str):
        raise ValueError("Bot name must be a string.")

    if not name.strip():
        raise ValueError("Bot name cannot be empty.")

    # Проверка на наличие спецсимволов в имени
    if any(char in string.punctuation for char in name):
        raise ValueError("Bot name cannot contain special characters.")

    # Проверка длины
    if len(name) > 255:
        raise ValueError("Bot name cannot exceed 255 characters.")

    return name.strip()


def validate_metadata_key(key: str) -> str:
    """
    Проверка валидности ключа метаданных.
    Ключ не должен быть пустым и не может превышать 255 символов.

    Args:
        key (str): Ключ метаданных.

    Returns:
        str: Валидированный ключ метаданных.

    Raises:
        ValueError: Если ключ метаданных пустой или слишком длинный.
    """
    if not isinstance(key, str):
        raise ValueError("Metadata key must be a string.")

    if not key.strip():
        raise ValueError("Metadata key cannot be empty.")

    # Проверка на длину ключа
    if len(key) > 255:
        raise ValueError("Metadata key cannot exceed 255 characters.")

    return key.strip()


def validate_metadata_value(value: str) -> str:
    """
    Проверка валидности значения метаданных.
    Значение не должно быть пустым.

    Args:
        value (str): Значение метаданных.

    Returns:
        str: Валидированное значение метаданных.

    Raises:
        ValueError: Если значение метаданных пустое.
    """
    if not isinstance(value, str):
        raise ValueError("Metadata value must be a string.")

    if not value.strip():
        raise ValueError("Metadata value cannot be empty.")

    return value.strip()


def validate_metadata(metadata_data: dict):
    """
    Валидация метаданных, включающая проверку ключа и значения.

    Args:
        metadata_data (dict): Данные метаданных для проверки.

    Raises:
        ValueError: Если метаданные некорректны.
    """
    # Валидация ключа и значения метаданных
    validate_metadata_key(metadata_data.get("metadata_key"))
    validate_metadata_value(metadata_data.get("metadata_value"))


def validate_status(status: str) -> str:
    """
    Проверка валидности статуса бота.
    Статус должен быть одним из допустимых: "active", "inactive", "paused".

    Args:
        status (str): Статус бота.

    Returns:
        str: Валидированный статус.

    Raises:
        ValueError: Если статус недопустимый.
    """
    valid_statuses = ["active", "inactive", "paused"]
    if status not in valid_statuses:
        raise ValueError(
            f"Invalid status: '{status}'. Must be one of {valid_statuses}."
        )

    return status


def validate_bot_id(bot_id: int) -> int:
    """
    Проверка валидности ID бота.
    ID должен быть положительным числом.

    Args:
        bot_id (int): ID бота.

    Returns:
        int: Валидированный ID бота.

    Raises:
        ValueError: Если ID бота не положительный.
    """
    if not isinstance(bot_id, int) or bot_id <= 0:
        raise ValueError(f"Invalid bot ID: {bot_id}. Must be a positive integer.")

    return bot_id


def validate_user_id(user_id: int) -> int:
    """
    Проверка валидности ID пользователя.
    ID должен быть положительным числом.

    Args:
        user_id (int): ID пользователя.

    Returns:
        int: Валидированный ID пользователя.

    Raises:
        ValueError: Если ID пользователя не положительный.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user ID: {user_id}. Must be a positive integer.")

    return user_id


def validate_block_ids(block_ids: list) -> list:
    """
    Проверка валидности списка ID блоков.
    Каждый блок должен иметь положительный целочисленный ID.

    Args:
        block_ids (list): Список ID блоков.

    Returns:
        list: Валидированный список ID блоков.

    Raises:
        ValueError: Если какой-либо ID блока не положительный.
    """
    if not isinstance(block_ids, list):
        raise ValueError("Block IDs must be provided as a list.")

    for idx, block_id in enumerate(block_ids):
        if not isinstance(block_id, int) or block_id <= 0:
            raise ValueError(
                f"Invalid block ID at index {idx}: {block_id}. Must be a positive integer."
            )

    return block_ids


async def validate_migrations_for_bot(bot_id: int):
    """
    Проверка состояния миграций для базы данных бота.

    Args:
        bot_id (int): ID бота для проверки состояния миграций.

    Raises:
        MigrationException: Если миграции для базы данных бота не были применены.
    """
    try:
        migrations_status = await check_migrations_status(bot_id)
        if migrations_status != "healthy":
            raise MigrationException(f"Migrations are pending for bot {bot_id}.")
    except Exception as e:
        raise MigrationException(
            f"Error checking migrations for bot {bot_id}: {str(e)}"
        )
