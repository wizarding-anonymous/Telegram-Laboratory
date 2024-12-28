from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base
from sqlalchemy.orm import relationship


class ApiRequest(Base):
    """
    Model for storing api request block information.
    """

    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False, default="make_request")
    method = Column(String(10), nullable=False, default="GET")
    url = Column(String(2048), nullable=False)
    headers = Column(JSON, nullable=True)
    params = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    connections = relationship("Connection",
                                 primaryjoin="ApiRequest.id==Connection.source_block_id",
                                 cascade="all, delete-orphan",
                                 lazy="selectin",
                                 )


    def __repr__(self):
        return f"<ApiRequest(id={self.id}, type='{self.type}', method='{self.method}', url='{self.url}')>"