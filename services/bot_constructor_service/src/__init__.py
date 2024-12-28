"""
Initialization module for the Bot Constructor microservice.

This module sets up the necessary components and imports for the microservice.
"""

__version__ = "1.0.0"
__author__ = "Your Name or Team"

# Import main components to simplify access
from .app import app
from .config import settings
from .db.database import init_db, close_engine, check_db_connection
from .integrations.redis_client import redis_client

__all__ = ["app", "settings", "init_db", "close_engine", "check_db_connection", "redis_client"]