# services\data_storage_service\src\integrations\logging_client.py
import os
import sys

from loguru import logger


class LoggingClient:
    """
    Клиент для централизованного логирования операций микросервиса.
    """

    def __init__(self, service_name: str = "DataStorageService"):
        """
        Инициализация клиента для логирования.

        Args:
            service_name (str): Имя микросервиса, которое будет указано в логах.
        """
        self.service_name = service_name
        self._setup_logger()
        logger.info(f"LoggingClient initialized for service: {self.service_name}")

    def _setup_logger(self):
        """
        Настройка логирования.
        """
        log_file = os.getenv("LOG_FILE_PATH", "./logs/data_storage_service.log")

        # Устанавливаем форматирование для логов
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        # Создаем директорию для логов, если она не существует
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Настроим логирование в файл
        logger.add(
            log_file,
            format=log_format,
            level="INFO",
            rotation="1 week",
            retention="30 days",
        )
        # Логирование в консоль
        logger.add(sys.stdout, format=log_format, level="DEBUG")

    def log_info(self, message: str, **kwargs):
        """
        Логирует информационное сообщение.

        Args:
            message (str): Сообщение для логирования.
            **kwargs: Дополнительные параметры для логирования.
        """
        logger.info(self._format_message(message, **kwargs))

    def log_warning(self, message: str, **kwargs):
        """
        Логирует предупреждающее сообщение.

        Args:
            message (str): Сообщение для логирования.
            **kwargs: Дополнительные параметры для логирования.
        """
        logger.warning(self._format_message(message, **kwargs))

    def log_error(self, message: str, **kwargs):
        """
        Логирует сообщение об ошибке.

        Args:
            message (str): Сообщение для логирования.
            **kwargs: Дополнительные параметры для логирования.
        """
        logger.error(self._format_message(message, **kwargs))

    def log_critical(self, message: str, **kwargs):
        """
        Логирует критическое сообщение.

        Args:
            message (str): Сообщение для логирования.
            **kwargs: Дополнительные параметры для логирования.
        """
        logger.critical(self._format_message(message, **kwargs))

    def log_debug(self, message: str, **kwargs):
        """
        Логирует отладочное сообщение.

        Args:
            message (str): Сообщение для логирования.
            **kwargs: Дополнительные параметры для логирования.
        """
        logger.debug(self._format_message(message, **kwargs))

    def _format_message(self, message: str, **kwargs) -> str:
        """
        Форматирует сообщение для логирования с дополнительной информацией.

        Args:
            message (str): Сообщение для логирования.
            **kwargs: Дополнительные параметры для логирования.

        Returns:
            str: Отформатированное сообщение.
        """
        extra_info = " | ".join(f"{key}={value}" for key, value in kwargs.items())
        return f"[{self.service_name}] {message}" + (
            f" | {extra_info}" if extra_info else ""
        )

    def log_migration_error(self, bot_id: int, error_message: str):
        """
        Логирует ошибку миграции для базы данных бота.

        Args:
            bot_id (int): ID бота, для которого произошла ошибка миграции.
            error_message (str): Сообщение об ошибке миграции.
        """
        logger.error(f"Migration error for bot {bot_id}: {error_message}")

    def log_migration_success(self, bot_id: int):
        """
        Логирует успешное применение миграций для базы данных бота.

        Args:
            bot_id (int): ID бота, для которого были успешно применены миграции.
        """
        logger.info(f"Migration successful for bot {bot_id}")
