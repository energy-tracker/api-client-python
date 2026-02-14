"""Device data models for Energy Tracker API."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DeviceSummaryDto:
    """Summary of a measuring device.

    Attributes:
        id: Unique identifier of the measuring device.
        name: Human-readable name of the measuring device.
        folder_path: Logical path for grouping the device into folders.
        last_updated_at: Timestamp of the last update, or None if never updated.
    """

    id: str
    name: str
    folder_path: str
    last_updated_at: datetime | None = None

    @classmethod
    def _from_dict(cls, data: dict) -> DeviceSummaryDto:
        last_updated_at = None
        if data.get("lastUpdatedAt"):
            last_updated_at = datetime.fromisoformat(data["lastUpdatedAt"])

        return cls(
            id=data["id"],
            name=data["name"],
            folder_path=data["folderPath"],
            last_updated_at=last_updated_at,
        )
