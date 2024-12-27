import os
import sys
from loguru import logger


class LoggingClient:
    def __init__(self, service_name: str):
        self.service_name = service_name
        # Удаляем все существующие обработчики
        logger.remove()
        self._setup_logger()
        logger.info(f"LoggingClient initialized for service: {self.service_name}")

    def _setup_logger(self):
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
            " | <cyan>service={extra[service_name]}</cyan>"
        )

        # Добавляем только один обработчик для файла
        logger.add(
            sink=sys.stdout,
            format=log_format,
            level="DEBUG",
            enqueue=True,
            filter=self._filter_by_service,
            
        )

    def _filter_by_service(self, record):
        """Filter log records to only include the configured service name."""
        record["extra"]["service_name"] = self.service_name
        return True
        
    def debug(self, message: str, *args, **kwargs) -> None:
        """Logs a message with DEBUG level."""
        logger.debug(message, *args, **kwargs, service_name=self.service_name)

    def info(self, message: str, *args, **kwargs) -> None:
        """Logs a message with INFO level."""
        logger.info(message, *args, **kwargs, service_name=self.service_name)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Logs a message with WARNING level."""
        logger.warning(message, *args, **kwargs, service_name=self.service_name)

    def error(self, message: str, *args, **kwargs) -> None:
        """Logs a message with ERROR level."""
        logger.error(message, *args, **kwargs, service_name=self.service_name)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Logs a message with CRITICAL level."""
        logger.critical(message, *args, **kwargs, service_name=self.service_name)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """Logs an exception with ERROR level."""
        logger.exception(message, *args, **kwargs, service_name=self.service_name)