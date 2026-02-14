"""Tests for Energy Tracker API data models."""

from datetime import datetime
from decimal import Decimal

from energy_tracker_api.models import (
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
    TimestampDto,
)


class TestTimestampDto:
    """Tests for TimestampDto."""

    def test_to_dict(self):
        # Arrange
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        dto = TimestampDto(timestamp=timestamp)

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {"timestamp": "2024-01-15T10:30:45.123"}


class TestDeviceSummaryDto:
    """Tests for DeviceSummaryDto."""

    def test_from_dict_with_all_fields(self):
        # Arrange
        data = {
            "id": "device-123",
            "name": "Gas Meter",
            "folderPath": "/basement/gas",
            "lastUpdatedAt": "2024-01-15T10:30:45.123Z",
        }

        # Act
        result = DeviceSummaryDto._from_dict(data)

        # Assert
        assert result.id == "device-123"
        assert result.name == "Gas Meter"
        assert result.folder_path == "/basement/gas"
        assert result.last_updated_at is not None

    def test_from_dict_without_last_updated(self):
        # Arrange
        data = {
            "id": "device-123",
            "name": "Gas Meter",
            "folderPath": "/basement/gas",
            "lastUpdatedAt": None,
        }

        # Act
        result = DeviceSummaryDto._from_dict(data)

        # Assert
        assert result.id == "device-123"
        assert result.last_updated_at is None

    def test_from_dict_without_last_updated_key(self):
        # Arrange
        data = {
            "id": "device-123",
            "name": "Gas Meter",
            "folderPath": "/basement/gas",
        }

        # Act
        result = DeviceSummaryDto._from_dict(data)

        # Assert
        assert result.last_updated_at is None


class TestMeterReadingDto:
    """Tests for MeterReadingDto (v3 response)."""

    def test_from_dict_with_all_fields(self):
        # Arrange
        data = {
            "timestamp": "2024-01-15T10:30:45.123Z",
            "value": "123.45",
            "rolloverOffset": 0,
            "meterId": "meter-abc",
            "note": "Manual reading",
            "meterNumber": "ABC-123",
        }

        # Act
        result = MeterReadingDto._from_dict(data)

        # Assert
        assert result.value == Decimal("123.45")
        assert result.rollover_offset == 0
        assert result.meter_id == "meter-abc"
        assert result.note == "Manual reading"
        assert result.meter_number == "ABC-123"

    def test_from_dict_without_optional_fields(self):
        # Arrange
        data = {
            "timestamp": "2024-01-15T10:30:45.123Z",
            "value": "999.99",
            "rolloverOffset": 100,
            "meterId": "meter-abc",
        }

        # Act
        result = MeterReadingDto._from_dict(data)

        # Assert
        assert result.value == Decimal("999.99")
        assert result.note is None
        assert result.meter_number is None

    def test_from_dict_preserves_decimal_precision(self):
        # Arrange
        data = {
            "timestamp": "2024-01-15T10:30:45.123Z",
            "value": "12345.67890",
            "rolloverOffset": 0,
            "meterId": "meter-abc",
        }

        # Act
        result = MeterReadingDto._from_dict(data)

        # Assert
        assert result.value == Decimal("12345.67890")


class TestCreateMeterReadingDto:
    """Tests for CreateMeterReadingDto (v3 request)."""

    def test_to_dict_value_is_string(self):
        # Arrange
        dto = CreateMeterReadingDto(value=Decimal("123.45"))

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {"value": "123.45"}
        assert isinstance(result["value"], str)

    def test_to_dict_with_all_fields(self):
        # Arrange
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        dto = CreateMeterReadingDto(
            value=Decimal("123.45"), timestamp=timestamp, note="Manual reading"
        )

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {
            "value": "123.45",
            "timestamp": "2024-01-15T10:30:45.123",
            "note": "Manual reading",
        }

    def test_to_dict_without_optional_fields(self):
        # Arrange
        dto = CreateMeterReadingDto(value=Decimal("0"))

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {"value": "0"}


class TestExportMeterReadingsDto:
    """Tests for ExportMeterReadingsDto."""

    def test_to_dict_with_defaults(self):
        # Arrange
        dto = ExportMeterReadingsDto(columns=[ExportColumn.DATE, ExportColumn.VALUE])

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {
            "columns": ["date", "value"],
            "includeHeader": True,
            "delimiter": "comma",
            "dateFormat": "iso",
        }

    def test_to_dict_with_custom_options(self):
        # Arrange
        dto = ExportMeterReadingsDto(
            columns=[ExportColumn.DATE, ExportColumn.VALUE, ExportColumn.NOTE],
            include_header=False,
            delimiter=CsvDelimiter.SEMICOLON,
            date_format=DateFormat.UNIX,
        )

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {
            "columns": ["date", "value", "note"],
            "includeHeader": False,
            "delimiter": "semicolon",
            "dateFormat": "unix",
        }

    def test_to_dict_with_all_columns(self):
        # Arrange
        dto = ExportMeterReadingsDto(
            columns=[
                ExportColumn.DATE,
                ExportColumn.VALUE,
                ExportColumn.NOTE,
                ExportColumn.METER_ID,
                ExportColumn.METER_NUMBER,
            ]
        )

        # Act
        result = dto._to_dict()

        # Assert
        assert result["columns"] == ["date", "value", "note", "meter_id", "meter_number"]


class TestEnvironmentEntryDto:
    """Tests for EnvironmentEntryDto."""

    def test_from_dict(self):
        # Arrange
        data = {
            "timestamp": "2024-01-15T10:30:45.123Z",
            "value": 23.5,
        }

        # Act
        result = EnvironmentEntryDto._from_dict(data)

        # Assert
        assert result.value == 23.5
        assert result.timestamp is not None


class TestEnvironmentRecordDto:
    """Tests for EnvironmentRecordDto."""

    def test_from_dict_with_entries(self):
        # Arrange
        data = {
            "id": "env-123",
            "title": "Temperature",
            "unit": "°C",
            "entries": [
                {"timestamp": "2024-01-15T10:00:00.000Z", "value": 22.0},
                {"timestamp": "2024-01-15T11:00:00.000Z", "value": 23.5},
            ],
        }

        # Act
        result = EnvironmentRecordDto._from_dict(data)

        # Assert
        assert result.id == "env-123"
        assert result.title == "Temperature"
        assert result.unit == "°C"
        assert len(result.entries) == 2
        assert result.entries[0].value == 22.0
        assert result.entries[1].value == 23.5

    def test_from_dict_without_unit(self):
        # Arrange
        data = {
            "id": "env-123",
            "title": "Temperature",
            "entries": [],
        }

        # Act
        result = EnvironmentRecordDto._from_dict(data)

        # Assert
        assert result.unit is None
        assert result.entries == []


class TestCreateEnvironmentRecordDto:
    """Tests for CreateEnvironmentRecordDto."""

    def test_to_dict_with_unit(self):
        # Arrange
        dto = CreateEnvironmentRecordDto(title="Temperature", unit="°C")

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {"title": "Temperature", "unit": "°C"}

    def test_to_dict_without_unit(self):
        # Arrange
        dto = CreateEnvironmentRecordDto(title="Temperature")

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {"title": "Temperature"}


class TestCreateEnvironmentEntryDto:
    """Tests for CreateEnvironmentEntryDto."""

    def test_to_dict_with_value_only(self):
        # Arrange
        dto = CreateEnvironmentEntryDto(value=23.5)

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {"value": 23.5}

    def test_to_dict_with_timestamp(self):
        # Arrange
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        dto = CreateEnvironmentEntryDto(value=23.5, timestamp=timestamp)

        # Act
        result = dto._to_dict()

        # Assert
        assert result == {
            "value": 23.5,
            "timestamp": "2024-01-15T10:30:45.123",
        }
