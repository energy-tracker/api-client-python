"""Environment record data models for Energy Tracker API."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EnvironmentEntryDto:
    """An environment measurement entry.

    Attributes:
        timestamp: Date and time when the entry was recorded.
        value: Value of the environmental record entry.
    """

    timestamp: datetime
    value: float

    @classmethod
    def _from_dict(cls, data: dict) -> EnvironmentEntryDto:
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            value=data["value"],
        )


@dataclass(frozen=True, slots=True)
class EnvironmentRecordDto:
    """An environment record with its entries.

    Attributes:
        id: Unique identifier of the environment record.
        title: Title of the environment record.
        entries: List of measurement entries.
        unit: Unit of measurement, or None if not set.
    """

    id: str
    title: str
    entries: list[EnvironmentEntryDto]
    unit: str | None = None

    @classmethod
    def _from_dict(cls, data: dict) -> EnvironmentRecordDto:
        return cls(
            id=data["id"],
            title=data["title"],
            unit=data.get("unit"),
            entries=[EnvironmentEntryDto._from_dict(e) for e in data.get("entries", [])],
        )


@dataclass(frozen=True, slots=True)
class CreateEnvironmentRecordDto:
    """DTO for creating a new environment record.

    Attributes:
        title: Title of the environment record (e.g., Temperature).
        unit: Unit of measurement (e.g., °C). Optional.
    """

    title: str
    unit: str | None = None

    def _to_dict(self) -> dict:
        data: dict[str, str] = {"title": self.title}

        if self.unit is not None:
            data["unit"] = self.unit

        return data


@dataclass(frozen=True, slots=True)
class CreateEnvironmentEntryDto:
    """DTO for creating a new environment measurement entry.

    Attributes:
        value: Numeric value of the environment measurement.
        timestamp: Optional timestamp (ISO 8601, UTC). Server uses current time if omitted.
    """

    value: float
    timestamp: datetime | None = None

    def _to_dict(self) -> dict:
        data: dict[str, float | str] = {"value": self.value}

        if self.timestamp is not None:
            data["timestamp"] = self.timestamp.isoformat(timespec="milliseconds")

        return data
