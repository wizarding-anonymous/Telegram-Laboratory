from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base
from sqlalchemy.orm import relationship


class Webhook(Base):
    """
    Model for storing webhook block information.
    """

    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False, default="set_webhook")
    url = Column(String(2048), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    connections = relationship("Connection",
                                 primaryjoin="Webhook.id==Connection.source_block_id",
                                 cascade="all, delete-orphan",
                                 lazy="selectin",
                                 )


    def __repr__(self):
        return f"<Webhook(id={self.id}, type='{self.type}', url='{self.url}')>"