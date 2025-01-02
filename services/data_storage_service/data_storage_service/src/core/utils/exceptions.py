"""
Custom exceptions for the Data Storage Service.
"""

class DatabaseException(Exception):
    """
    Custom exception for database-related errors.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Database Error: {self.message}"


class ServiceDiscoveryException(Exception):
    """
    Custom exception for errors related to the Service Discovery service.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Service Discovery Error: {self.message}"


class ValidationException(Exception):
    """
    Custom exception for data validation errors.
    """
    def __init__(self, message: str):
         self.message = message
         super().__init__(self.message)

    def __str__(self):
         return f"Validation Error: {self.message}"