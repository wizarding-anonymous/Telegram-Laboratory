from typing import Optional


class MetricError(Exception):
    """Base exception for metrics-related errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class MetricCollectionError(MetricError):
    """Raised when metric collection fails."""
    pass


class MetricStorageError(MetricError):
    """Raised when storing metrics fails."""
    pass


class MetricNotFoundError(MetricError):
    """Raised when requested metric is not found."""
    pass


class MetricValidationError(MetricError):
    """Raised when metric data validation fails."""
    pass


class MetricAggregationError(MetricError):
    """Raised when metric aggregation fails."""
    pass


class MetricThresholdError(MetricError):
    """Raised when metric exceeds defined thresholds."""

    def __init__(self, message: str, metric_name: str, current_value: float, threshold: float):
        super().__init__(message, {
            "metric_name": metric_name,
            "current_value": current_value,
            "threshold": threshold
        })


class MetricTypeError(MetricError):
    """Raised when metric type is invalid."""
    pass


class MetricPeriodError(MetricError):
    """Raised when metric time period is invalid."""
    pass
