"""Energy Tracker API Client for Python."""

from importlib.metadata import version

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

__version__ = version("energy-tracker-api")
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
