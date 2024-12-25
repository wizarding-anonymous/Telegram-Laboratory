# services\api_gateway\src\core\utils\helpers.py
from typing import Any, Dict, Optional, Union
import json
from datetime import datetime, date
import re
from uuid import UUID
from decimal import Decimal

from aiohttp import web
import structlog
from multidict import CIMultiDict, MultiDict

from src.core.exceptions import ValidationError


logger = structlog.get_logger(__name__)


def setup_request_id(request: web.Request, request_id: Optional[str] = None) -> str:
    """Setup unique request ID for tracing.
    
    Args:
        request: aiohttp request object
        request_id: Optional custom request ID
        
    Returns:
        str: Request ID
    """
    if request_id is None:
        request_id = request.headers.get("X-Request-ID", str(UUID.uuid4()))
    request["request_id"] = request_id
    return request_id


def get_request_id(request: web.Request) -> Optional[str]:
    """Get request ID from request object.
    
    Args:
        request: aiohttp request object
        
    Returns:
        Optional[str]: Request ID if set
    """
    return request.get("request_id")


def setup_correlation_id(
    request: web.Request,
    correlation_id: Optional[str] = None
) -> str:
    """Setup correlation ID for request tracing across services.
    
    Args:
        request: aiohttp request object
        correlation_id: Optional custom correlation ID
        
    Returns:
        str: Correlation ID
    """
    if correlation_id is None:
        correlation_id = request.headers.get("X-Correlation-ID", str(UUID.uuid4()))
    request["correlation_id"] = correlation_id
    return correlation_id


def get_correlation_id(request: web.Request) -> Optional[str]:
    """Get correlation ID from request object.
    
    Args:
        request: aiohttp request object
        
    Returns:
        Optional[str]: Correlation ID if set
    """
    return request.get("correlation_id")


def prepare_query_params(params: Union[MultiDict, Dict[str, Any]]) -> Dict[str, Any]:
    """Convert query parameters to a standardized format.
    
    Args:
        params: Request query parameters
        
    Returns:
        Dict[str, Any]: Processed query parameters
    """
    result = {}
    for key, value in params.items():
        if isinstance(value, (list, tuple)):
            result[key] = [_process_param_value(v) for v in value]
        else:
            result[key] = _process_param_value(value)
    return result


def _process_param_value(value: str) -> Any:
    """Process individual query parameter value.
    
    Args:
        value: Parameter value to process
        
    Returns:
        Any: Processed value
    """
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null":
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def prepare_headers(
    headers: Union[CIMultiDict, Dict[str, str]],
    exclude: Optional[list[str]] = None
) -> Dict[str, str]:
    """Prepare headers for forwarding to downstream services.
    
    Args:
        headers: Original request headers
        exclude: Optional list of headers to exclude
        
    Returns:
        Dict[str, str]: Processed headers
    """
    if exclude is None:
        exclude = []
    
    exclude = [h.lower() for h in exclude]
    result = {}
    
    for key, value in headers.items():
        if key.lower() not in exclude:
            result[key] = value
            
    return result


def json_serializer(obj: Any) -> str:
    """Custom JSON serializer for handling special types.
    
    Args:
        obj: Object to serialize
        
    Returns:
        str: JSON serialized string
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def parse_json_body(body: str) -> Dict[str, Any]:
    """Safely parse JSON request body.
    
    Args:
        body: JSON string to parse
        
    Returns:
        Dict[str, Any]: Parsed JSON data
        
    Raises:
        ValidationError: If JSON is invalid
    """
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse JSON body", error=str(e), body=body[:200])
        raise ValidationError("Invalid JSON body")


def validate_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data for logging.
    
    Args:
        data: Dictionary containing potentially sensitive data
        
    Returns:
        Dict[str, Any]: Data with sensitive fields masked
    """
    sensitive_fields = {
        "password", "token", "access_token", "refresh_token",
        "secret", "key", "authorization", "cookie"
    }
    
    result = {}
    for key, value in data.items():
        if any(field in key.lower() for field in sensitive_fields):
            result[key] = "***" if value else value
        elif isinstance(value, dict):
            result[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            result[key] = [
                mask_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def extract_client_info(request: web.Request) -> Dict[str, str]:
    """Extract client information from request.
    
    Args:
        request: aiohttp request object
        
    Returns:
        Dict[str, str]: Client information
    """
    return {
        "ip": request.remote,
        "user_agent": request.headers.get("User-Agent", "Unknown"),
        "referer": request.headers.get("Referer", "Unknown"),
    }


def get_forward_headers(request: web.Request) -> Dict[str, str]:
    """Get headers that should be forwarded to downstream services.
    
    Args:
        request: aiohttp request object
        
    Returns:
        Dict[str, str]: Headers to forward
    """
    forward_headers = {
        "X-Request-ID": get_request_id(request),
        "X-Correlation-ID": get_correlation_id(request),
        "X-Forwarded-For": request.remote,
        "X-Forwarded-Proto": request.scheme,
        "X-Forwarded-Host": request.host,
    }
    
    # Add original authorization if present
    auth_header = request.headers.get("Authorization")
    if auth_header:
        forward_headers["Authorization"] = auth_header
        
    return forward_headers


def build_error_response(
    message: str,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build standardized error response.
    
    Args:
        message: Error message
        code: Optional error code
        details: Optional error details
        
    Returns:
        Dict[str, Any]: Error response structure
    """
    response = {
        "error": {
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if code:
        response["error"]["code"] = code
        
    if details:
        response["error"]["details"] = details
        
    return response