# services\api_gateway\src\core\utils\validators.py
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import re
from uuid import UUID
import ipaddress
from decimal import Decimal
import json

import structlog
from multidict import MultiDict

from src.core.exceptions import ValidationError


logger = structlog.get_logger(__name__)


class RequestValidator:
    """Base class for request validators."""
    
    def __init__(self, field_name: str):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
        """
        self.field_name = field_name

    def __call__(self, value: Any) -> Any:
        """Validate the value.
        
        Args:
            value: Value to validate
            
        Returns:
            Any: Validated and possibly transformed value
            
        Raises:
            ValidationError: If validation fails
        """
        raise NotImplementedError


class RequiredValidator(RequestValidator):
    """Validator that ensures a field is present and not None."""
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            raise ValidationError(f"Field '{self.field_name}' is required")
        return value


class TypeValidator(RequestValidator):
    """Validator that ensures a field is of the correct type."""
    
    def __init__(self, field_name: str, expected_type: type):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            expected_type: Expected type of the field
        """
        super().__init__(field_name)
        self.expected_type = expected_type

    def __call__(self, value: Any) -> Any:
        if value is not None and not isinstance(value, self.expected_type):
            try:
                return self.expected_type(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Field '{self.field_name}' must be of type {self.expected_type.__name__}"
                )
        return value


class RangeValidator(RequestValidator):
    """Validator that ensures a numeric value is within a specified range."""
    
    def __init__(
        self,
        field_name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None
    ):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            min_value: Optional minimum allowed value
            max_value: Optional maximum allowed value
        """
        super().__init__(field_name)
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value: Union[int, float]) -> Union[int, float]:
        if value is None:
            return value
            
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                f"Field '{self.field_name}' must be greater than or equal to {self.min_value}"
            )
            
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                f"Field '{self.field_name}' must be less than or equal to {self.max_value}"
            )
            
        return value


class RegexValidator(RequestValidator):
    """Validator that ensures a string matches a regular expression pattern."""
    
    def __init__(self, field_name: str, pattern: str, error_message: Optional[str] = None):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            pattern: Regex pattern to match against
            error_message: Optional custom error message
        """
        super().__init__(field_name)
        self.pattern = re.compile(pattern)
        self.error_message = error_message or f"Field '{field_name}' has invalid format"

    def __call__(self, value: str) -> str:
        if value is not None and not self.pattern.match(value):
            raise ValidationError(self.error_message)
        return value


class LengthValidator(RequestValidator):
    """Validator that ensures a string or list is of the correct length."""
    
    def __init__(
        self,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            min_length: Optional minimum allowed length
            max_length: Optional maximum allowed length
        """
        super().__init__(field_name)
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value: Union[str, list]) -> Union[str, list]:
        if value is None:
            return value
            
        length = len(value)
        
        if self.min_length is not None and length < self.min_length:
            raise ValidationError(
                f"Field '{self.field_name}' must be at least {self.min_length} characters long"
            )
            
        if self.max_length is not None and length > self.max_length:
            raise ValidationError(
                f"Field '{self.field_name}' must be at most {self.max_length} characters long"
            )
            
        return value


class EmailValidator(RequestValidator):
    """Validator for email addresses."""
    
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    def __call__(self, value: str) -> str:
        if value is not None and not re.match(self.EMAIL_PATTERN, value):
            raise ValidationError(f"Field '{self.field_name}' must be a valid email address")
        return value


class UUIDValidator(RequestValidator):
    """Validator for UUID strings."""
    
    def __call__(self, value: str) -> str:
        if value is not None:
            try:
                UUID(value)
            except ValueError:
                raise ValidationError(f"Field '{self.field_name}' must be a valid UUID")
        return value


class IPAddressValidator(RequestValidator):
    """Validator for IP addresses."""
    
    def __call__(self, value: str) -> str:
        if value is not None:
            try:
                ipaddress.ip_address(value)
            except ValueError:
                raise ValidationError(f"Field '{self.field_name}' must be a valid IP address")
        return value


class JsonValidator(RequestValidator):
    """Validator for JSON strings."""
    
    def __call__(self, value: str) -> Union[Dict, List]:
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError(f"Field '{self.field_name}' must be valid JSON")
        return value


class EnumValidator(RequestValidator):
    """Validator that ensures a value is one of a set of choices."""
    
    def __init__(self, field_name: str, choices: List[Any]):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            choices: List of valid choices
        """
        super().__init__(field_name)
        self.choices = choices

    def __call__(self, value: Any) -> Any:
        if value is not None and value not in self.choices:
            choices_str = ", ".join(str(c) for c in self.choices)
            raise ValidationError(
                f"Field '{self.field_name}' must be one of: {choices_str}"
            )
        return value


class DecimalValidator(RequestValidator):
    """Validator for decimal numbers."""
    
    def __init__(
        self,
        field_name: str,
        precision: Optional[int] = None,
        scale: Optional[int] = None
    ):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            precision: Optional total number of digits
            scale: Optional number of decimal places
        """
        super().__init__(field_name)
        self.precision = precision
        self.scale = scale

    def __call__(self, value: Union[str, Decimal]) -> Decimal:
        if value is None:
            return value
            
        try:
            decimal_value = Decimal(str(value))
        except (ValueError, decimal.InvalidOperation):
            raise ValidationError(f"Field '{self.field_name}' must be a valid decimal number")
            
        if self.precision is not None:
            str_value = str(decimal_value)
            digits = str_value.replace('.', '')
            if len(digits) > self.precision:
                raise ValidationError(
                    f"Field '{self.field_name}' must have at most {self.precision} total digits"
                )
                
        if self.scale is not None:
            scale = -decimal_value.as_tuple().exponent
            if scale > self.scale:
                raise ValidationError(
                    f"Field '{self.field_name}' must have at most {self.scale} decimal places"
                )
                
        return decimal_value


class DateTimeValidator(RequestValidator):
    """Validator for datetime strings."""
    
    def __init__(self, field_name: str, format: str = "%Y-%m-%dT%H:%M:%S"):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            format: Expected datetime format string
        """
        super().__init__(field_name)
        self.format = format

    def __call__(self, value: str) -> datetime:
        if value is not None:
            try:
                return datetime.strptime(value, self.format)
            except ValueError:
                raise ValidationError(
                    f"Field '{self.field_name}' must be a valid datetime in format {self.format}"
                )
        return value


def validate_request_data(
    data: Dict[str, Any],
    validators: Dict[str, List[RequestValidator]]
) -> Dict[str, Any]:
    """Validate request data using provided validators.
    
    Args:
        data: Request data to validate
        validators: Dictionary mapping field names to lists of validators
        
    Returns:
        Dict[str, Any]: Validated and transformed data
        
    Raises:
        ValidationError: If validation fails for any field
    """
    validated_data = {}
    errors = {}
    
    for field_name, field_validators in validators.items():
        value = data.get(field_name)
        
        try:
            for validator in field_validators:
                value = validator(value)
            if value is not None:
                validated_data[field_name] = value
        except ValidationError as e:
            errors[field_name] = str(e)
            
    if errors:
        raise ValidationError("Validation failed", details=errors)
        
    return validated_data


def validate_query_params(
    params: MultiDict,
    validators: Dict[str, List[RequestValidator]]
) -> Dict[str, Any]:
    """Validate query parameters using provided validators.
    
    Args:
        params: Query parameters to validate
        validators: Dictionary mapping parameter names to lists of validators
        
    Returns:
        Dict[str, Any]: Validated and transformed parameters
        
    Raises:
        ValidationError: If validation fails for any parameter
    """
    return validate_request_data(dict(params), validators)