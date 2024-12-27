from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Log(Base):
    """
    Модель для хранения логов системы.
    """
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    service = Column(String(255), nullable=False, index=True)
    level = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    metadata = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Log(service={self.service}, level={self.level}, timestamp={self.timestamp})>"
