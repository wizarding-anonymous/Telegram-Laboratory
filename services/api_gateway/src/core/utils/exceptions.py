"""
Custom exceptions for the API Gateway service.
"""

from fastapi import HTTPException
from typing import Any


class GatewayException(HTTPException):
    """
    Base exception for API Gateway specific errors.
    """

    def __init__(self, status_code: int, detail: str, headers: dict[str, Any] | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class RouteNotFoundException(GatewayException):
    """
    Exception raised when a route is not found in the routing configuration.
    """
    def __init__(self, detail: str = "Route not found", headers: dict[str, Any] | None = None):
        super().__init__(status_code=404, detail=detail, headers=headers)


class ServiceUnavailableException(GatewayException):
    """
    Exception raised when a downstream service is unavailable.
    """
    def __init__(self, detail: str = "Service unavailable", headers: dict[str, Any] | None = None):
         super().__init__(status_code=503, detail=detail, headers=headers)


class AuthenticationException(GatewayException):
    """
    Exception raised when authentication fails.
    """
    def __init__(self, detail: str = "Authentication failed", headers: dict[str, Any] | None = None):
         super().__init__(status_code=401, detail=detail, headers=headers)


class AuthorizationException(GatewayException):
     """
     Exception raised when authorization fails.
     """
     def __init__(self, detail: str = "Authorization failed", headers: dict[str, Any] | None = None):
         super().__init__(status_code=403, detail=detail, headers=headers)


class InvalidRequestException(GatewayException):
    """
    Exception raised when the request data is invalid.
    """
    def __init__(self, detail: str = "Invalid request data", headers: dict[str, Any] | None = None):
        super().__init__(status_code=400, detail=detail, headers=headers)


class IntegrationException(GatewayException):
    """
    Exception raised when an error occurs during integration with another service.
    """

    def __init__(self, detail: str, headers: dict[str, Any] | None = None, status_code: int = 500):
         super().__init__(status_code=status_code, detail=detail, headers=headers)


class ConfigurationException(GatewayException):
    """
    Exception raised when there is an issue with configuration settings.
    """
    def __init__(self, detail: str = "Configuration error", headers: dict[str, Any] | None = None):
        super().__init__(status_code=500, detail=detail, headers=headers)


class RateLimitExceededException(GatewayException):
    """
    Exception raised when the rate limit is exceeded.
    """
    def __init__(self, detail: str = "Rate limit exceeded", headers: dict[str, Any] | None = None):
         super().__init__(status_code=429, detail=detail, headers=headers)

class BadRequestException(GatewayException):
    """
    Exception raised for bad requests
    """
    def __init__(self, detail: str, headers: dict[str, Any] | None = None):
        super().__init__(status_code=400, detail=detail, headers=headers)

class InternalServerError(GatewayException):
    """
    Exception raised for internal server errors
    """
    def __init__(self, detail: str, headers: dict[str, Any] | None = None):
         super().__init__(status_code=500, detail=detail, headers=headers)

class ServiceDiscoveryException(GatewayException):
     """
     Exception raised when an error occurs during service discovery.
     """
     def __init__(self, detail: str = "Service discovery error", headers: dict[str, Any] | None = None):
         super().__init__(status_code=500, detail=detail, headers=headers)