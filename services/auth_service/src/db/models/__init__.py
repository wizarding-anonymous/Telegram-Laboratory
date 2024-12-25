# services/auth_service/src/db/models/__init__.py

from .base import Base
from .user_model import User
from .role_model import Role
from .session_model import Session
from .association import user_roles  # Импортируем таблицу ассоциаций

__all__ = ["Base", "User", "Role", "Session", "user_roles"]