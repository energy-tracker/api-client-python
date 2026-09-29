"""Models for daily values and calendar interval extrapolations."""

import math
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class CalculationInterval(StrEnum):
    """Calendar interval for extrapolation; weeks begin on Monday."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class ExtrapolationMethod(StrEnum):
    """Available server-side extrapolation methods."""

    STANDARD = "standard"


def _number(value: object, field: str, *, duration: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be a JSON number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    if duration and number < 0:
        raise ValueError(f"{field} must not be negative")
    return number


@dataclass(frozen=True, slots=True)
class CalculationPointDto:
    """Consumption or production for a calendar interval, in the device unit.

    Attributes:
        date: Interval start in UTC.
        actual_value: Value derived from recorded readings by interpolation.
        actual_duration: Reading-backed duration in seconds, affected by DST.
        expected_value: Estimated total for the interval; do not add actual_value.
        expected_duration: Nominal duration in seconds, using 24 hours per calendar day.
    """

    date: datetime
    actual_value: float
    actual_duration: float
    expected_value: float
    expected_duration: float

    @classmethod
    def _from_dict(cls, data: dict) -> CalculationPointDto:
        date = datetime.fromisoformat(data["date"])
        if date.utcoffset() is None:
            raise ValueError("date must include a UTC offset")
        return cls(
            date=date.astimezone(UTC),
            actual_value=_number(data["actualValue"], "actualValue"),
            actual_duration=_number(data["actualDuration"], "actualDuration", duration=True),
            expected_value=_number(data["expectedValue"], "expectedValue"),
            expected_duration=_number(data["expectedDuration"], "expectedDuration", duration=True),
        )
