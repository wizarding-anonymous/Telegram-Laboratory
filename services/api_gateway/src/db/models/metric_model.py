# services\api_gateway\src\db\models\metric_model.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import String, DateTime, Float, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PgUUID

from src.db.base import Base

class Metric(Base):
    """Model for storing system and service metrics."""
    __tablename__ = "metrics"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    service_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    metric_value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    tags: Mapped[dict] = mapped_column(
        JSON,
        nullable=True
    )

    # Performance metrics
    response_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    requests_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0,
        nullable=True
    )

    error_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0,
        nullable=True
    )

    success_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    # Resource metrics
    cpu_usage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    memory_usage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"Metric(id={self.id}, "
            f"service={self.service_name}, "
            f"name={self.metric_name}, "
            f"value={self.metric_value})"
        )

    @property
    def metric_key(self) -> str:
        """Generate unique key for the metric."""
        return f"{self.service_name}:{self.metric_name}"