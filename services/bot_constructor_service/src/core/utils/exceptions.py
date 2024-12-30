"""
Custom exceptions for the Bot Constructor microservice.

This module defines custom exception classes to handle specific
error conditions within the application. These exceptions are used
to provide more specific and informative error messages to clients
and to facilitate better error handling within the service.
"""

from fastapi import HTTPException


class BotConstructorException(HTTPException):
    """
    Base class for all custom exceptions in the Bot Constructor service.
    """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class BlockNotFoundException(BotConstructorException):
    """
    Exception raised when a block with the given ID is not found.
    """
    def __init__(self, block_id: int):
        super().__init__(status_code=404, detail=f"Block with id: {block_id} not found")


class BotNotFoundException(BotConstructorException):
    """
    Exception raised when a bot with the given ID is not found.
    """
    def __init__(self, bot_id: int):
        super().__init__(status_code=404, detail=f"Bot with id: {bot_id} not found")


class ConnectionNotFoundException(BotConstructorException):
    """
    Exception raised when a connection with the given ID is not found.
    """
    def __init__(self, connection_id: int):
         super().__init__(status_code=404, detail=f"Connection with id: {connection_id} not found")

class InvalidBlockTypeException(BotConstructorException):
    """
    Exception raised when an invalid block type is provided.
    """
    def __init__(self, block_type: str):
        super().__init__(status_code=400, detail=f"Invalid block type: {block_type}")


class InvalidBotIdException(BotConstructorException):
    """
    Exception raised when an invalid bot ID is provided.
    """
    def __init__(self, bot_id: int):
         super().__init__(status_code=400, detail=f"Invalid bot id: {bot_id}")

class InvalidBotNameException(BotConstructorException):
    """
    Exception raised when an invalid bot name is provided.
    """
    def __init__(self, bot_name: str):
          super().__init__(status_code=400, detail=f"Invalid bot name: {bot_name}")


class InvalidContentException(BotConstructorException):
     """
     Exception raised when invalid content is provided
     """
     def __init__(self, content: str):
         super().__init__(status_code=400, detail=f"Invalid content: {content}")

class InvalidConnectionsException(BotConstructorException):
    """
    Exception raised when invalid connections are provided
    """
    def __init__(self, connections: list):
         super().__init__(status_code=400, detail=f"Invalid connections: {connections}")


class InvalidWebhookUrlException(BotConstructorException):
     """
     Exception raised when an invalid webhook URL is provided.
     """
     def __init__(self, url: str):
         super().__init__(status_code=400, detail=f"Invalid webhook URL: {url}")


class InvalidChatIdException(BotConstructorException):
     """
     Exception raised when an invalid chat ID is provided.
     """
     def __init__(self, chat_id: int):
         super().__init__(status_code=400, detail=f"Invalid chat ID: {chat_id}")

class InvalidPermissionException(BotConstructorException):
     """
     Exception raised when an invalid permission is provided.
     """
     def __init__(self, permission: str):
         super().__init__(status_code=400, detail=f"Invalid permission: {permission}")


class InvalidUserIdException(BotConstructorException):
    """
    Exception raised when an invalid user ID is provided.
    """
    def __init__(self, user_id: int):
         super().__init__(status_code=400, detail=f"Invalid user ID: {user_id}")

class InvalidBlockIdsException(BotConstructorException):
     """
     Exception raised when invalid block ids are provided
     """
     def __init__(self, block_ids: list):
         super().__init__(status_code=400, detail=f"Invalid block IDs: {block_ids}")

class InvalidStatusException(BotConstructorException):
     """
     Exception raised when an invalid status is provided
     """
     def __init__(self, status: str):
        super().__init__(status_code=400, detail=f"Invalid status: {status}")

class InvalidVersionException(BotConstructorException):
      """
      Exception raised when an invalid version is provided
      """
      def __init__(self, version: str):
        super().__init__(status_code=400, detail=f"Invalid version: {version}")

class TelegramAPIException(BotConstructorException):
    """
    Exception raised when a Telegram API error occurs.
    """
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Telegram API Error: {detail}")

class AuthServiceException(BotConstructorException):
    """
    Exception raised when an Auth Service error occurs.
    """
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Auth Service Error: {detail}")

class RedisConnectionException(BotConstructorException):
    """
    Exception raised when a Redis connection error occurs.
    """
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Redis Connection Error: {detail}")

class DatabaseException(BotConstructorException):
     """
     Exception raised when a database related error occurs
     """
     def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Database Error: {detail}")


class LoggingException(BotConstructorException):
    """
    Exception raised when a Logging service error occurs
    """
    def __init__(self, detail: str):
          super().__init__(status_code=500, detail=f"Logging Error: {detail}")
class FlowChartException(BotConstructorException):
    """
    Exception raised when Flow Chart error occurs
    """
    def __init__(self, detail: str):
      super().__init__(status_code=400, detail=f"Flow Chart Error: {detail}")


class TemplateNotFoundException(BotConstructorException):
  """
  Exception raised when template not found
  """
  def __init__(self, template_id: int):
    super().__init__(status_code=404, detail=f"Template with id: {template_id} not found")


class InvalidTokenException(BotConstructorException):
  """
  Exception raised when token is invalid
  """
  def __init__(self, detail: str):
    super().__init__(status_code=401, detail=f"Invalid token: {detail}")

__all__ = [
    "BotConstructorException",
    "BlockNotFoundException",
    "BotNotFoundException",
    "ConnectionNotFoundException",
    "InvalidBlockTypeException",
    "InvalidBotIdException",
    "InvalidBotNameException",
    "InvalidContentException",
    "InvalidConnectionsException",
    "InvalidWebhookUrlException",
    "InvalidChatIdException",
    "InvalidPermissionException",
    "InvalidUserIdException",
    "InvalidBlockIdsException",
    "InvalidStatusException",
    "InvalidVersionException",
    "TelegramAPIException",
    "AuthServiceException",
    "RedisConnectionException",
    "DatabaseException",
    "LoggingException",
     "FlowChartException",
     "TemplateNotFoundException",
     "InvalidTokenException"
]