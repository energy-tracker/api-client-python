"""Common data models for Energy Tracker API."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TimestampDto:
    """DTO containing a single timestamp.

    Used for deletion operations that identify entries by timestamp.

    Attributes:
        timestamp: Date and time of the entry (ISO 8601, UTC).
    """

    timestamp: datetime

    def _to_dict(self) -> dict:
        return {"timestamp": self.timestamp.isoformat(timespec="milliseconds")}
