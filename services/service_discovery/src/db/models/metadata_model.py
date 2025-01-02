from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON
from .base import Base


class Metadata(Base):
    """
    SQLAlchemy model for storing metadata of a service in the database.
    """

    __tablename__ = "service_metadata"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    def __repr__(self):
        return f"<Metadata(id={self.id}, service_id='{self.service_id}')>"