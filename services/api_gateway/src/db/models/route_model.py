# services\api_gateway\src\db\models\route_model.py
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PgUUID

from src.db.base import Base


class Route(Base):
    """
    Model for storing API route configurations.
    
    This model represents the routing configuration for the API Gateway,
    storing information about service endpoints and their configurations.
    """
    __tablename__ = "routes"
    
    # Primary key using UUID
    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    
    # Service identification
    service_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    
    # Route configuration
    path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    upstream_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # Authorization configuration
    requires_auth: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    allowed_roles: Mapped[Optional[List[str]]] = mapped_column(
        nullable=True,
    )
    
    # Rate limiting configuration
    rate_limit: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    rate_limit_period: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    
    # Caching configuration
    cache_enabled: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    cache_ttl: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    
    # Monitoring and metadata
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    def __repr__(self) -> str:
        """String representation of the Route model."""
        return (
            f"Route(id={self.id}, "
            f"service_name='{self.service_name}', "
            f"path='{self.path}', "
            f"method='{self.method}')"
        )
    
    @property
    def route_key(self) -> str:
        """Generate a unique key for the route based on path and method."""
        return f"{self.method.upper()}:{self.path}"
    
    def to_dict(self) -> dict:
        """Convert the route model to a dictionary."""
        return {
            "id": str(self.id),
            "service_name": self.service_name,
            "path": self.path,
            "method": self.method,
            "upstream_url": self.upstream_url,
            "requires_auth": self.requires_auth,
            "allowed_roles": self.allowed_roles,
            "rate_limit": self.rate_limit,
            "rate_limit_period": self.rate_limit_period,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }