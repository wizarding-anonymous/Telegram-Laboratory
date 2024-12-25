# services\api_gateway\src\db\models\service_model.py
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy import String, DateTime, Boolean, JSON, Enum, func, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PgUUID, ARRAY
import enum

from src.db.base import Base

class ServiceStatus(str, enum.Enum):
   HEALTHY = "healthy"
   DEGRADED = "degraded" 
   UNHEALTHY = "unhealthy"
   STARTING = "starting"
   STOPPING = "stopping"
   MAINTENANCE = "maintenance"

class Service(Base):
   """Model for storing registered service information."""
   __tablename__ = "services"

   id: Mapped[UUID] = mapped_column(
       PgUUID(as_uuid=True),
       primary_key=True,
       server_default=func.gen_random_uuid(),
   )

   name: Mapped[str] = mapped_column(
       String(100),
       nullable=False,
       unique=True,
       index=True
   )

   host: Mapped[str] = mapped_column(
       String(255),
       nullable=False
   )

   port: Mapped[int] = mapped_column(
       Integer,
       nullable=False
   )

   status: Mapped[ServiceStatus] = mapped_column(
       Enum(ServiceStatus),
       default=ServiceStatus.STARTING,
       nullable=False
   )

   health_check_url: Mapped[str] = mapped_column(
       String(255),
       nullable=True
   )

   version: Mapped[str] = mapped_column(
       String(50),
       nullable=True
   )

   metadata: Mapped[dict] = mapped_column(
       JSON,
       nullable=True
   )
   
   endpoints: Mapped[List[str]] = mapped_column(
       ARRAY(String),  
       nullable=True
   )

   last_health_check: Mapped[datetime] = mapped_column(
       DateTime(timezone=True),
       nullable=True
   )

   consecutive_failures: Mapped[int] = mapped_column(
       Integer,
       default=0,
       nullable=False
   )

   weight: Mapped[int] = mapped_column(
       Integer,
       default=1,
       nullable=False
   )

   is_active: Mapped[bool] = mapped_column(
       Boolean,
       default=True,
       nullable=False
   )

   def __repr__(self) -> str:
       return (
           f"Service(id={self.id}, "
           f"name='{self.name}', "
           f"host='{self.host}', "
           f"port={self.port}, "
           f"status={self.status.value})"
       )

   @property
   def url(self) -> str:
       """Get service URL."""
       return f"http://{self.host}:{self.port}"

   @property 
   def is_healthy(self) -> bool:
       """Check if service is healthy."""
       return self.status == ServiceStatus.HEALTHY

   def update_health_status(
       self,
       is_healthy: bool,
       check_time: Optional[datetime] = None
   ) -> None:
       """Update service health status.
       
       Args:
           is_healthy: Health check result
           check_time: Time of health check
       """
       if is_healthy:
           self.status = ServiceStatus.HEALTHY
           self.consecutive_failures = 0
       else:
           self.consecutive_failures += 1
           if self.consecutive_failures >= 3:
               self.status = ServiceStatus.UNHEALTHY
           else:
               self.status = ServiceStatus.DEGRADED
               
       self.last_health_check = check_time or datetime.utcnow()