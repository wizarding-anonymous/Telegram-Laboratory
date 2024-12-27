# services\api_gateway\src\core\exceptions\service.py
from typing import Optional, Dict, Any


class ServiceError(Exception):
    """Base exception for service-related errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class ServiceNotFoundError(ServiceError):
    """Raised when service is not found."""

    def __init__(self, service_id: str):
        super().__init__(
            f"Service {service_id} not found",
            {"service_id": service_id}
        )


class ServiceRegistrationError(ServiceError):
    """Raised when service registration fails."""

    def __init__(self, message: str, service_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, {"service_data": service_data})


class ServiceValidationError(ServiceError):
    """Raised when service data validation fails."""

    def __init__(self, message: str, validation_errors: Dict[str, str]):
        super().__init__(message, {"validation_errors": validation_errors})


class ServiceHealthCheckError(ServiceError):
    """Raised when service health check fails."""

    def __init__(self, service_name: str, reason: str):
        super().__init__(
            f"Health check failed for {service_name}: {reason}",
            {"service_name": service_name, "reason": reason}
        )


class ServiceAlreadyExistsError(ServiceError):
    """Raised when attempting to register duplicate service."""

    def __init__(self, service_name: str):
        super().__init__(
            f"Service {service_name} already exists",
            {"service_name": service_name}
        )


class ServiceDeregistrationError(ServiceError):
    """Raised when service deregistration fails."""

    def __init__(self, service_id: str, reason: str):
        super().__init__(
            f"Failed to deregister service {service_id}: {reason}",
            {"service_id": service_id, "reason": reason}
        )


class ServiceUpdateError(ServiceError):
    """Raised when service update fails."""

    def __init__(
        self,
        service_id: str,
        reason: str,
        update_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            f"Failed to update service {service_id}: {reason}",
            {"service_id": service_id, "reason": reason, "update_data": update_data}
        )
