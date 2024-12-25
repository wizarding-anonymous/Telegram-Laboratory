# services\api_gateway\src\core\exceptions\proxy.py
from typing import Optional


class ProxyError(Exception):
    """Base exception for proxy-related errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class UpstreamServiceError(ProxyError):
    """Raised when upstream service returns an error."""

    def __init__(self, message: str, status_code: int, service_name: str):
        super().__init__(message, {
            "status_code": status_code,
            "service_name": service_name
        })


class RouteNotFoundError(ProxyError):
    """Raised when no matching route is found."""

    def __init__(self, path: str, method: str):
        super().__init__(
            f"No route found for {method} {path}",
            {"path": path, "method": method}
        )


class ServiceUnavailableError(ProxyError):
    """Raised when upstream service is unavailable."""

    def __init__(self, service_name: str, reason: Optional[str] = None):
        super().__init__(
            f"Service {service_name} is unavailable",
            {"service_name": service_name, "reason": reason}
        )


class CircuitBreakerError(ProxyError):
    """Raised when circuit breaker is open."""

    def __init__(self, service_name: str, failure_count: int):
        super().__init__(
            f"Circuit breaker is open for {service_name}",
            {"service_name": service_name, "failure_count": failure_count}
        )


class RateLimitExceededError(ProxyError):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit: int, window: int):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window} seconds",
            {"limit": limit, "window": window}
        )


class TimeoutError(ProxyError):
    """Raised when request times out."""

    def __init__(self, service_name: str, timeout: float):
        super().__init__(
            f"Request to {service_name} timed out after {timeout} seconds",
            {"service_name": service_name, "timeout": timeout}
        )
