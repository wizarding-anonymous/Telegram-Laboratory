# services\auth_service\src\integrations\logging_client.py


import os
import sys
from loguru import logger


class LoggingClient:
    def __init__(self, service_name: str = "AuthService"):
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
        )

        # Добавляем только один обработчик для файла
        logger.add(
            sink=sys.stdout,
            format=log_format,
            level="DEBUG",
            enqueue=True
        )