from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base


class Connection(Base):
    """
    Model for storing connections between blocks.
    """
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    source_block_id = Column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False, index=True)
    target_block_id = Column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False, index=True)

    def __repr__(self):
         return f"<Connection(source_block_id={self.source_block_id}, target_block_id='{self.target_block_id}')>"