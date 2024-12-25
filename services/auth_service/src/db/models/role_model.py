# services/auth_service/src/db/models/role_model.py

from enum import Enum
from typing import Dict, List, Set
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from .base import Base
from .association import user_roles

class RoleType(str, Enum):
    """Enumeration of built-in role types"""
    ADMIN = "admin"
    USER = "user"

class Permission(str, Enum):
    """Enumeration of available permissions"""
    # User management permissions
    READ_USERS = "read:users"
    CREATE_USERS = "create:users"
    UPDATE_USERS = "update:users"
    DELETE_USERS = "delete:users"
    
    # Role management permissions
    READ_ROLES = "read:roles"
    CREATE_ROLES = "create:roles"
    UPDATE_ROLES = "update:roles"
    DELETE_ROLES = "delete:roles"
    
    # Bot management permissions
    READ_BOTS = "read:bots"
    CREATE_BOTS = "create:bots"
    UPDATE_BOTS = "update:bots"
    DELETE_BOTS = "delete:bots"
    
    # Session management permissions
    READ_SESSIONS = "read:sessions"
    DELETE_SESSIONS = "delete:sessions"

class Role(Base):
    """Role model with predefined roles and permissions"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    permissions = Column(JSON, nullable=False)

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin"  # Используем "selectin" для оптимальной загрузки
    )

    # Predefined role configurations
    PREDEFINED_ROLES: Dict[str, List[str]] = {
        RoleType.ADMIN: [perm.value for perm in Permission],  # All permissions
        RoleType.USER: [
            Permission.READ_BOTS.value,
            Permission.CREATE_BOTS.value,
            Permission.UPDATE_BOTS.value,
            Permission.DELETE_BOTS.value,
            Permission.READ_SESSIONS.value,
            Permission.DELETE_SESSIONS.value
        ]
    }

    @classmethod
    def get_default_permissions(cls, role_name: str) -> List[str]:
        """
        Get default permissions for a predefined role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            List of permissions for the role
        """
        return cls.PREDEFINED_ROLES.get(role_name, [])

    @classmethod
    def is_predefined_role(cls, role_name: str) -> bool:
        """
        Check if a role name corresponds to a predefined role.
        
        Args:
            role_name: Name to check
            
        Returns:
            True if role is predefined, False otherwise
        """
        return role_name in cls.PREDEFINED_ROLES

    @classmethod
    def get_all_predefined_roles(cls) -> Set[str]:
        """
        Get all predefined role names.
        
        Returns:
            Set of predefined role names
        """
        return set(cls.PREDEFINED_ROLES.keys())

    def has_permission(self, permission: str) -> bool:
        """
        Check if role has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        return permission in self.permissions

    def has_any_permission(self, permissions: List[str]) -> bool:
        """
        Check if role has any of the specified permissions.
        
        Args:
            permissions: List of permissions to check
            
        Returns:
            True if role has any of the permissions, False otherwise
        """
        return bool(set(self.permissions) & set(permissions))

    def has_all_permissions(self, permissions: List[str]) -> bool:
        """
        Check if role has all specified permissions.
        
        Args:
            permissions: List of permissions to check
            
        Returns:
            True if role has all permissions, False otherwise
        """
        return set(permissions).issubset(set(self.permissions))

    def __repr__(self) -> str:
        """String representation of the role"""
        return f"<Role(id={self.id}, name='{self.name}', permissions_count={len(self.permissions)})>"