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
from .models import (
    CreateEnvironmentEntryDto,
    CreateEnvironmentRecordDto,
    CreateMeterReadingDto,
    CsvDelimiter,
    DateFormat,
    DeviceSummaryDto,
    EnvironmentEntryDto,
    EnvironmentRecordDto,
    ExportColumn,
    ExportMeterReadingsDto,
    MeterReadingDto,
    SortDirection,
    TimestampDto,
)

__version__ = "2.0.0"
__all__ = [
    "EnergyTrackerClient",
    # Models
    "CreateMeterReadingDto",
    "MeterReadingDto",
    "ExportMeterReadingsDto",
    "SortDirection",
    "CsvDelimiter",
    "DateFormat",
    "ExportColumn",
    "DeviceSummaryDto",
    "CreateEnvironmentRecordDto",
    "CreateEnvironmentEntryDto",
    "EnvironmentRecordDto",
    "EnvironmentEntryDto",
    "TimestampDto",
    # Exceptions
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
