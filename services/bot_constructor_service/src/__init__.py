# services\bot_constructor_service\src\__init__.py
"""
Initialization module for the Bot Constructor microservice.

This module sets up the necessary components and imports for the microservice.
"""

__version__ = "1.0.0"
__author__ = "Your Name or Team"

# Import main components to simplify access
from .app import app

__all__ = ["app"]
