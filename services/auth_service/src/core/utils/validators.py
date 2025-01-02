import re
from src.core.utils.exceptions import ValidationException


def validate_email(email: str) -> None:
    """
    Validates the email address.
    """
    if not email:
        raise ValidationException("Email cannot be empty")
    if not isinstance(email, str):
        raise ValidationException("Email must be a string")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationException("Invalid email format")


def validate_password(password: str) -> None:
    """
    Validates the password.
    """
    if not password:
        raise ValidationException("Password cannot be empty")
    if not isinstance(password, str):
         raise ValidationException("Password must be a string")
    if len(password) < 6:
          raise ValidationException("Password must be at least 6 characters long")

def validate_token(token: str) -> None:
    """
    Validates the JWT token.
    """
    if not token:
       raise ValidationException("Token cannot be empty")
    if not isinstance(token, str):
        raise ValidationException("Token must be a string")
    if len(token) > 1000:
       raise ValidationException("Token is too long (max 1000 characters)")