# services\api_gateway\src\api\schemas\route_schema.py
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(str, Enum):
    NONE = "none"
    JWT = "jwt"
    API_KEY = "api_key"


class ServiceHealthCheck(BaseModel):
    endpoint: str = Field(..., description="Health check endpoint for the service")
    interval_seconds: int = Field(default=30, description="Interval between health checks in seconds")
    timeout_seconds: int = Field(default=5, description="Timeout for health check requests")
    healthy_threshold: int = Field(default=2, description="Number of consecutive successful checks to mark as healthy")
    unhealthy_threshold: int = Field(default=3, description="Number of consecutive failed checks to mark as unhealthy")


class RateLimitConfig(BaseModel):
    requests_per_second: int = Field(..., description="Maximum number of requests allowed per second")
    burst_size: int = Field(..., description="Maximum burst size for requests")
    timeframe_seconds: int = Field(default=1, description="Time window for rate limiting in seconds")


class CircuitBreakerConfig(BaseModel):
    failure_threshold: int = Field(default=5, description="Number of failures before circuit opens")
    success_threshold: int = Field(default=3, description="Number of successes before circuit closes")
    timeout_seconds: int = Field(default=60, description="Time circuit stays open before trying again")
    half_open_timeout: int = Field(default=30, description="Timeout for half-open state")


class RetryConfig(BaseModel):
    max_attempts: int = Field(default=3, description="Maximum number of retry attempts")
    initial_delay_ms: int = Field(default=1000, description="Initial delay between retries in milliseconds")
    max_delay_ms: int = Field(default=5000, description="Maximum delay between retries in milliseconds")
    multiplier: float = Field(default=2.0, description="Multiplier for exponential backoff")
    retry_on_status_codes: List[int] = Field(
        default=[500, 502, 503, 504],
        description="HTTP status codes that trigger retry"
    )


class CacheConfig(BaseModel):
    enabled: bool = Field(default=False, description="Enable caching for this route")
    ttl_seconds: int = Field(default=300, description="Time to live for cached responses")
    cache_control: Optional[str] = Field(default=None, description="Cache-Control header value")
    vary_by_headers: List[str] = Field(default_factory=list, description="Headers to vary cache by")
    vary_by_query_params: List[str] = Field(default_factory=list, description="Query parameters to vary cache by")


class TransformConfig(BaseModel):
    request_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Headers to add/modify in the request"
    )
    response_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Headers to add/modify in the response"
    )
    request_template: Optional[str] = Field(
        default=None,
        description="Template for transforming request body"
    )
    response_template: Optional[str] = Field(
        default=None,
        description="Template for transforming response body"
    )


class UpstreamService(BaseModel):
    name: str = Field(..., description="Name of the upstream service")
    url: str = Field(..., description="Base URL of the upstream service")
    weight: Optional[int] = Field(default=1, description="Weight for load balancing")
    health_check: Optional[ServiceHealthCheck] = Field(
        default=None,
        description="Health check configuration"
    )


class RouteConfig(BaseModel):
    id: str = Field(..., description="Unique identifier for the route")
    path: str = Field(..., description="URL path pattern for the route")
    method: HttpMethod = Field(..., description="HTTP method for the route")
    auth_type: AuthType = Field(default=AuthType.NONE, description="Authentication type required")
    upstream_services: List[UpstreamService] = Field(
        ...,
        description="List of upstream services for this route"
    )
    rate_limit: Optional[RateLimitConfig] = Field(
        default=None,
        description="Rate limiting configuration"
    )
    circuit_breaker: Optional[CircuitBreakerConfig] = Field(
        default=None,
        description="Circuit breaker configuration"
    )
    retry_policy: Optional[RetryConfig] = Field(
        default=None,
        description="Retry policy configuration"
    )
    cache_config: Optional[CacheConfig] = Field(
        default=None,
        description="Caching configuration"
    )
    transform_config: Optional[TransformConfig] = Field(
        default=None,
        description="Request/Response transformation configuration"
    )
    timeout_seconds: float = Field(
        default=30.0,
        description="Timeout for upstream requests in seconds"
    )
    cors_enabled: bool = Field(
        default=False,
        description="Enable CORS for this route"
    )
    active: bool = Field(
        default=True,
        description="Whether this route is active"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for organizing and filtering routes"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("path")
    def validate_path(cls, v):
        if not v.startswith("/"):
            raise ValueError("Path must start with /")
        return v

    @validator("upstream_services")
    def validate_upstream_services(cls, v):
        if not v:
            raise ValueError("At least one upstream service is required")
        total_weight = sum(service.weight or 1 for service in v)
        if total_weight <= 0:
            raise ValueError("Total weight of upstream services must be positive")
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": "user-service-route",
                "path": "/api/v1/users/{user_id}",
                "method": "GET",
                "auth_type": "jwt",
                "upstream_services": [
                    {
                        "name": "user-service",
                        "url": "http://user-service:8080",
                        "weight": 1,
                        "health_check": {
                            "endpoint": "/health",
                            "interval_seconds": 30,
                            "timeout_seconds": 5
                        }
                    }
                ],
                "rate_limit": {
                    "requests_per_second": 100,
                    "burst_size": 50
                },
                "timeout_seconds": 30.0,
                "cors_enabled": True,
                "tags": ["users", "api"]
            }
        }


class RouteList(BaseModel):
    routes: List[RouteConfig]
    total_count: int = Field(..., description="Total number of routes")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=50, description="Number of items per page")