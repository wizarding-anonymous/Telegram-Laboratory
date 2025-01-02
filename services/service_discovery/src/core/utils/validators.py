import re
from src.core.utils.exceptions import ValidationException


def validate_service_name(service_name: str) -> None:
    """
    Validates the service name.
    """
    if not service_name:
        raise ValidationException("Service name cannot be empty")
    if not isinstance(service_name, str):
        raise ValidationException("Service name must be a string")
    if len(service_name) > 255:
        raise ValidationException("Service name is too long (max 255 characters)")
    if not re.match(r"^[a-zA-Z0-9_-]+$", service_name):
        raise ValidationException(
            "Service name must contain only letters, numbers, underscores and hyphens"
        )


def validate_address(address: str) -> None:
    """
    Validates the service address.
    """
    if not address:
        raise ValidationException("Service address cannot be empty")
    if not isinstance(address, str):
        raise ValidationException("Service address must be a string")
    if len(address) > 255:
        raise ValidationException("Service address is too long (max 255 characters)")
    if not re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", address) and not re.match(r"^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$", address):
        raise ValidationException("Service address is invalid")


def validate_port(port: int) -> None:
     """
     Validates the service port.
     """
     if not isinstance(port, int):
         raise ValidationException("Port must be an integer")
     if not 0 < port < 65535:
          raise ValidationException("Port must be between 1 and 65535")

def validate_metadata(metadata: dict) -> None:
    """
    Validates the service metadata.
    """
    if not isinstance(metadata, dict):
        raise ValidationException("Metadata must be a dictionary")
    
    for key, value in metadata.items():
        if not isinstance(key, str):
            raise ValidationException(f"Metadata key '{key}' must be a string.")
        if not isinstance(value, (str, int, float, bool, dict, list)):
            raise ValidationException(f"Metadata value '{value}' must be a string, number, boolean, dict or list.")