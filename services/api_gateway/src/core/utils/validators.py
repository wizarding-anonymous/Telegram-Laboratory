"""
Validators for the API Gateway service.
"""
import re
from typing import Any
from fastapi import HTTPException
from src.core.utils.exceptions import InvalidRequestException
from loguru import logger


def validate_url(url: str) -> str:
    """
    Validates if a given string is a valid URL.

    Args:
        url: The string to validate.

    Returns:
        The valid URL if it passes validation.

    Raises:
        InvalidRequestException: If the string is not a valid URL.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain.name
        r'localhost|'   # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'  # ...or ip
        r'(?::\d+)?' # ...port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE) # ...and anything after the base url
    if not re.match(regex, url):
      logger.error(f"URL validation failed: {url} is not a valid URL.")
      raise InvalidRequestException(detail="Invalid URL format")
    return url

def validate_method(method: str) -> str:
    """
    Validates if a given string is a valid HTTP method.

    Args:
        method: The string to validate.

    Returns:
        The valid HTTP method in uppercase.

    Raises:
        InvalidRequestException: If the string is not a valid HTTP method.
    """
    valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    if method.upper() not in valid_methods:
        logger.error(f"Method validation failed: {method} is not a valid HTTP method.")
        raise InvalidRequestException(detail="Invalid HTTP method")
    return method.upper()


def validate_header_key(header_key: str) -> str:
    """
    Validates if a given string is a valid header key (alphanumeric, '-' and '_').

    Args:
        header_key: The string to validate.

    Returns:
        The valid header key.

    Raises:
        InvalidRequestException: If the string is not a valid header key.
    """
    regex = re.compile(r"^[a-zA-Z0-9_-]+$")
    if not re.match(regex, header_key):
       logger.error(f"Header key validation failed: {header_key} is not a valid header key.")
       raise InvalidRequestException(detail="Invalid header key format")
    return header_key


def validate_header_value(header_value: str) -> str:
    """
    Validates if a given string is a valid header value (no new lines, tabs, leading/trailing spaces).

    Args:
        header_value: The string to validate.

    Returns:
        The valid header value.

    Raises:
        InvalidRequestException: If the string is not a valid header value.
    """
    if "\n" in header_value or "\t" in header_value or header_value.strip() != header_value:
      logger.error(f"Header value validation failed: {header_value} is not a valid header value.")
      raise InvalidRequestException(detail="Invalid header value format")
    return header_value

def validate_status_code(status_code: int) -> int:
    """
    Validates if a given integer is a valid HTTP status code.

    Args:
        status_code: The integer to validate.

    Returns:
        The valid HTTP status code if it passes validation.

    Raises:
        InvalidRequestException: If the integer is not a valid HTTP status code.
    """
    if not 100 <= status_code <= 599:
       logger.error(f"Status code validation failed: {status_code} is not a valid HTTP status code.")
       raise InvalidRequestException(detail="Invalid HTTP status code")
    return status_code

def validate_json_data(data: str) -> Any:
    """
    Validates if given string is valid JSON data

    Args:
        data: string to validate

    Returns:
        A python dictionary if the data is valid

    Raises:
        InvalidRequestException: If the data is not valid json
    """
    try:
       import json
       return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON validation failed: {data} is not valid JSON. Details: {e}")
        raise InvalidRequestException(detail=f"Invalid JSON data format: {e}") from e

def validate_non_empty_string(string: str, field_name: str) -> str:
    """Validates that a string is not empty and returns it.

    Args:
       string: string to validate
       field_name: name of field for logging purposes

    Returns:
        The string if it passes validation

    Raises:
       InvalidRequestException: If string is empty
    """
    if not string or not string.strip():
      logger.error(f"Validation failed: {field_name} is empty or contains only whitespaces.")
      raise InvalidRequestException(detail=f"Invalid {field_name}: cannot be empty")
    return string

def validate_positive_integer(integer: int, field_name: str) -> int:
    """Validates that a integer is positive number

    Args:
        integer: integer to validate
        field_name: name of field for logging purposes

    Returns:
        The integer if it passes validation

    Raises:
        InvalidRequestException: if integer is not positive
    """
    if not isinstance(integer, int) or integer <= 0:
        logger.error(f"Validation failed: {field_name} must be positive integer")
        raise InvalidRequestException(detail=f"Invalid {field_name}: must be a positive integer.")
    return integer