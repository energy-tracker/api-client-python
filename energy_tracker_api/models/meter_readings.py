"""Meter reading data models for Energy Tracker API."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class SortDirection(StrEnum):
    """Sort direction for query results."""

    ASC = "asc"
    DESC = "desc"


class CsvDelimiter(StrEnum):
    """CSV delimiter options for export."""

    COMMA = "comma"
    SEMICOLON = "semicolon"
    TAB = "tab"


class DateFormat(StrEnum):
    """Date format options for CSV export."""

    ISO = "iso"
    DATE_TIME = "date_time"
    UNIX = "unix"
    UNIX_MS = "unix_ms"


class ExportColumn(StrEnum):
    """Available columns for CSV export."""

    DATE = "date"
    VALUE = "value"
    NOTE = "note"
    METER_ID = "meter_id"
    METER_NUMBER = "meter_number"


@dataclass(frozen=True, slots=True)
class MeterReadingDto:
    """A meter reading returned from the API.

    Attributes:
        timestamp: Date and time when the reading was recorded.
        value: Recorded meter reading value (decimal precision).
        rollover_offset: Rollover offset applied to the value.
        meter_id: Unique identifier of the associated meter.
        note: Optional note or comment about this reading.
        meter_number: Optional external meter number.
    """

    timestamp: datetime
    value: Decimal
    rollover_offset: float
    meter_id: str
    note: str | None = None
    meter_number: str | None = None

    @classmethod
    def _from_dict(cls, data: dict) -> MeterReadingDto:
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            value=Decimal(data["value"]),
            rollover_offset=data["rolloverOffset"],
            meter_id=data["meterId"],
            note=data.get("note"),
            meter_number=data.get("meterNumber"),
        )


@dataclass(frozen=True, slots=True)
class CreateMeterReadingDto:
    """DTO for creating a new meter reading.

    Attributes:
        value: Measured value to be recorded for the device.
        timestamp: Optional date and time when the reading was recorded (ISO 8601, UTC).
        note: Optional note or comment about this reading.
    """

    value: Decimal
    timestamp: datetime | None = None
    note: str | None = None

    def _to_dict(self) -> dict:
        data: dict[str, str] = {}

        data["value"] = str(self.value)

        if self.timestamp is not None:
            data["timestamp"] = self.timestamp.isoformat(timespec="milliseconds")

        if self.note is not None:
            data["note"] = self.note

        return data


@dataclass(frozen=True, slots=True)
class ExportMeterReadingsDto:
    """DTO for configuring meter reading CSV export.

    Attributes:
        columns: Columns and their order in the exported CSV file.
        include_header: Whether to include the header row (default: True).
        delimiter: CSV delimiter (default: comma).
        date_format: Date format in the export (default: iso).
    """

    columns: list[ExportColumn]
    include_header: bool = True
    delimiter: CsvDelimiter = CsvDelimiter.COMMA
    date_format: DateFormat = DateFormat.ISO

    def _to_dict(self) -> dict:
        return {
            "columns": list(self.columns),
            "includeHeader": self.include_header,
            "delimiter": self.delimiter,
            "dateFormat": self.date_format,
        }
