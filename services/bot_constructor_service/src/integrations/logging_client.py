# services\bot_constructor_service\src\integrations\logging_client.py
from loguru import logger


class LoggingClient:
    """
    Client for centralized logging of operations.
    """

    def __init__(self, service_name: str = "BotConstructor"):
        """
        Initialize the LoggingClient.

        Args:
            service_name (str): Name of the service to include in log entries.
        """
        self.service_name = service_name
        logger.info(f"LoggingClient initialized for service: {self.service_name}")

    def log_info(self, message: str, **kwargs):
        """
        Log an informational message.

        Args:
            message (str): The message to log.
            **kwargs: Additional key-value pairs to include in the log.
        """
        logger.info(self._format_message(message, **kwargs))

    def log_warning(self, message: str, **kwargs):
        """
        Log a warning message.

        Args:
            message (str): The message to log.
            **kwargs: Additional key-value pairs to include in the log.
        """
        logger.warning(self._format_message(message, **kwargs))

    def log_error(self, message: str, **kwargs):
        """
        Log an error message.

        Args:
            message (str): The message to log.
            **kwargs: Additional key-value pairs to include in the log.
        """
        logger.error(self._format_message(message, **kwargs))

    def log_critical(self, message: str, **kwargs):
        """
        Log a critical error message.

        Args:
            message (str): The message to log.
            **kwargs: Additional key-value pairs to include in the log.
        """
        logger.critical(self._format_message(message, **kwargs))

    def log_debug(self, message: str, **kwargs):
        """
        Log a debug message.

        Args:
            message (str): The message to log.
            **kwargs: Additional key-value pairs to include in the log.
        """
        logger.debug(self._format_message(message, **kwargs))

    def _format_message(self, message: str, **kwargs) -> str:
        """
        Format the log message with service name and additional context.

        Args:
            message (str): The message to log.
            **kwargs: Additional key-value pairs to include in the log.

        Returns:
            str: The formatted log message.
        """
        extra_info = " | ".join(f"{key}={value}" for key, value in kwargs.items())
        return f"[{self.service_name}] {message}" + (f" | {extra_info}" if extra_info else "")


# Example Usage
if __name__ == "__main__":
    logger_client = LoggingClient()

    # Logging various levels
    logger_client.log_info("This is an informational message", user_id=123, action="create_bot")
    logger_client.log_warning("This is a warning message", user_id=123, reason="low_disk_space")
    logger_client.log_error("This is an error message", user_id=123, error_code=500)
    logger_client.log_critical("This is a critical error message", user_id=123, service="database")
    logger_client.log_debug("This is a debug message", user_id=123, debug_info="connection_pool_status")
