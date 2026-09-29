"""Calculation response contract, including DST durations and malformed numbers."""

from datetime import UTC, datetime

import pytest

from energy_tracker_api import CalculationPointDto


@pytest.fixture
def point():
    return {
        "date": "2026-03-28T23:00:00.000Z",
        "actualValue": 4.2,
        "actualDuration": 82800,
        "expectedValue": 8.4,
        "expectedDuration": 86400,
    }


def test_point_preserves_values_and_dst_durations(point):
    result = CalculationPointDto._from_dict(point)
    assert result == CalculationPointDto(
        date=datetime(2026, 3, 28, 23, tzinfo=UTC),
        actual_value=4.2,
        actual_duration=82800.0,
        expected_value=8.4,
        expected_duration=86400.0,
    )


def test_partial_and_terminal_points_are_not_normalized(point):
    point.update(actualValue=-1.5, actualDuration=0, expectedValue=-3, expectedDuration=0)
    result = CalculationPointDto._from_dict(point)
    assert result.actual_value == -1.5
    assert result.expected_value == -3
    assert result.actual_duration == result.expected_duration == 0


def test_fractional_duration_is_preserved(point):
    point["actualDuration"] = 0.5
    assert CalculationPointDto._from_dict(point).actual_duration == 0.5


@pytest.mark.parametrize(
    "field", ["date", "actualValue", "actualDuration", "expectedValue", "expectedDuration"]
)
def test_every_field_is_required(point, field):
    del point[field]
    with pytest.raises(KeyError):
        CalculationPointDto._from_dict(point)


@pytest.mark.parametrize(
    "field", ["actualValue", "actualDuration", "expectedValue", "expectedDuration"]
)
@pytest.mark.parametrize("value", [True, "1.5", None, float("nan"), float("inf")])
def test_numbers_are_not_coerced_from_invalid_json_values(point, field, value):
    point[field] = value
    with pytest.raises((TypeError, ValueError)):
        CalculationPointDto._from_dict(point)


@pytest.mark.parametrize("field", ["actualDuration", "expectedDuration"])
def test_negative_durations_are_invalid(point, field):
    point[field] = -1
    with pytest.raises(ValueError):
        CalculationPointDto._from_dict(point)


@pytest.mark.parametrize("date", [None, "invalid", "2026-03-29", "2026-03-29T00:00:00"])
def test_response_dates_require_an_offset(point, date):
    point["date"] = date
    with pytest.raises((TypeError, ValueError)):
        CalculationPointDto._from_dict(point)
