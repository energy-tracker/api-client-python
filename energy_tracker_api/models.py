"""Data models for Energy Tracker API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateMeterReadingDto:
    """DTO for creating a new meter reading.

    Attributes:
        value: Measured value to be recorded for the device.
        timestamp: Optional date and time when the reading was recorded (ISO 8601, UTC).
        note: Optional note or comment about this reading.
    """

    value: float
    timestamp: Optional[datetime] = None
    note: Optional[str] = None

    def _to_dict(self) -> dict:
        data: dict[str, float | str] = {}

        data["value"] = self.value

        if self.timestamp is not None:
            data["timestamp"] = self.timestamp.isoformat(timespec="milliseconds")

        if self.note is not None:
            data["note"] = self.note

        return data
