"""Energy Tracker API Client for Python."""

from .client import EnergyTrackerClient
from .exceptions import (
    AuthenticationError,
    ConflictError,
    EnergyTrackerAPIError,
    ForbiddenError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)
from .models import CreateMeterReadingDto

__version__ = "1.0.0"
__all__ = [
    "EnergyTrackerClient",
    "CreateMeterReadingDto",
    "EnergyTrackerAPIError",
    "ValidationError",
    "AuthenticationError",
    "ForbiddenError",
    "ResourceNotFoundError",
    "ConflictError",
    "RateLimitError",
    "NetworkError",
    "TimeoutError",
]
