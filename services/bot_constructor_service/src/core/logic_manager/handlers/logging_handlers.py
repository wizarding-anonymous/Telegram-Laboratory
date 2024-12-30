from typing import Any, Dict
from src.core.utils import handle_exceptions
from src.core.logic_manager.handlers.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class LoggingHandler:
    """
    Handler for processing logging blocks.
    """

    def __init__(self):
        pass

    @handle_exceptions
    async def handle_log_message(
        self,
        block: Dict[str, Any],
        chat_id: int,
        variables: Dict[str, Any],
         user_message: str,
         bot_logic: Dict[str, Any],
    ) -> None:
        """Handles log message block."""
        content = block.get("content", {})
        logging_client.info(f"Handling log message block {block.get('id')} for chat_id: {chat_id}")
        message_template = content.get("message")
        level = content.get("level", "INFO").upper()

        if message_template:
            message = get_template(message_template).render(variables=variables)
            if level == "INFO":
                logging_client.info(f"Log message: {message}")
            elif level == "DEBUG":
                logging_client.debug(f"Log message: {message}")
            elif level == "WARNING":
                logging_client.warning(f"Log message: {message}")
            elif level == "ERROR":
                logging_client.error(f"Log message: {message}")
            elif level == "CRITICAL":
                logging_client.critical(f"Log message: {message}")
            else:
                logging_client.warning(f"Unsupported log level: {level}")
                return
        else:
            logging_client.warning("Log message or level was not provided")