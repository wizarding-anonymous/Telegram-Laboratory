import re
from src.core.utils.exceptions import ValidationException

def validate_bot_name(bot_name: str) -> None:
    """
    Validates the bot name.
    """
    if not bot_name:
        raise ValidationException("Bot name cannot be empty")
    if not isinstance(bot_name, str):
        raise ValidationException("Bot name must be a string")
    if len(bot_name) > 255:
         raise ValidationException("Bot name is too long (max 255 characters)")
    if not re.match(r"^[a-zA-Z0-9\s_-]+$", bot_name):
         raise ValidationException(
            "Bot name must contain only letters, numbers, spaces, underscores and hyphens"
        )
    
def validate_metadata_key(metadata_key: str) -> None:
    """
    Validates the metadata key.
    """
    if not metadata_key:
       raise ValidationException("Metadata key cannot be empty")
    if not isinstance(metadata_key, str):
        raise ValidationException("Metadata key must be a string")
    if len(metadata_key) > 255:
       raise ValidationException("Metadata key is too long (max 255 characters)")
    if not re.match(r"^[a-zA-Z0-9_-]+$", metadata_key):
         raise ValidationException(
            "Metadata key must contain only letters, numbers, underscores and hyphens"
        )