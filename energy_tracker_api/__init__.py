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
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)
from .models import (
    CalculationInterval,
    CalculationPointDto,
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
    ExtrapolationMethod,
    MeterReadingDto,
    SortDirection,
    TimestampDto,
    TokenScope,
    TokenStatusDto,
)

__version__ = version("energy-tracker-api")
__all__ = [
    "EnergyTrackerClient",
    # Models
    "CalculationInterval",
    "CalculationPointDto",
    "ExtrapolationMethod",
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
    "TokenScope",
    "TokenStatusDto",
    # Exceptions
    "EnergyTrackerAPIError",
    "ValidationError",
    "AuthenticationError",
    "ForbiddenError",
    "ResourceNotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServiceUnavailableError",
    "NetworkError",
    "TimeoutError",
]
