"""Exercise calculation requests and failure contracts through a real HTTP transport."""

import asyncio
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from unittest.mock import AsyncMock

import pytest
from aiohttp import web

from energy_tracker_api import (
    AuthenticationError,
    CalculationInterval,
    ConflictError,
    EnergyTrackerAPIError,
    EnergyTrackerClient,
    ForbiddenError,
    RateLimitError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)


@pytest.fixture(params=["daily_values", "extrapolations"])
def operation(request):
    return request.param


async def calculate(client, operation, **kwargs):
    if operation == "extrapolations":
        kwargs.setdefault("interval", CalculationInterval.MONTH)
    return await getattr(client.calculations, operation)("device-id", **kwargs)


async def test_default_requests_and_empty_results(serve, operation):
    async def handler(request):
        suffix = "daily-values" if operation == "daily_values" else "extrapolations/standard/month"
        assert request.method == "GET"
        assert request.path == f"/v1/devices/standard/device-id/{suffix}"
        assert request.query == {}
        assert request.headers["Authorization"] == "Bearer test-token"
        return web.json_response([])

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        assert await calculate(client, operation) == []


@pytest.mark.parametrize(
    "interval",
    [
        CalculationInterval.DAY,
        CalculationInterval.WEEK,
        CalculationInterval.MONTH,
        CalculationInterval.QUARTER,
        CalculationInterval.YEAR,
    ],
)
async def test_all_intervals_are_encoded_in_path(serve, interval):
    async def handler(request):
        assert (
            request.path
            == f"/v1/devices/standard/device-id/extrapolations/standard/{interval.value}"
        )
        return web.json_response([])

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        assert await client.calculations.extrapolations("device-id", interval=interval) == []


async def test_time_filters_preserve_instants_without_calendar_rounding(serve, operation):
    async def handler(request):
        assert dict(request.query) == {
            "from": "2026-03-28T23:15:12.123456+00:00",
            "to": "2026-03-29T22:45:23.456789+00:00",
            "timeZone": "Europe/Berlin",
        }
        return web.json_response([])

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        await calculate(
            client,
            operation,
            from_timestamp=datetime.fromisoformat("2026-03-29T00:15:12.123456+01:00"),
            to_timestamp=datetime.fromisoformat("2026-03-30T00:45:23.456789+02:00"),
            time_zone="Europe/Berlin",
        )


@pytest.mark.parametrize("microsecond", [1, 999, 1000, 123456, 999999])
async def test_time_filters_preserve_subsecond_range_at_midnight(serve, operation, microsecond):
    start = datetime(2026, 9, 1, tzinfo=UTC)
    end = start + timedelta(microseconds=microsecond)

    async def handler(request):
        transmitted_start = datetime.fromisoformat(request.query["from"])
        transmitted_end = datetime.fromisoformat(request.query["to"])
        assert transmitted_start == start
        assert transmitted_end == end
        assert transmitted_start < transmitted_end
        return web.json_response([])

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        await calculate(client, operation, from_timestamp=start, to_timestamp=end)


async def test_time_filters_serialize_exact_seconds_and_milliseconds(serve, operation):
    async def handler(request):
        assert dict(request.query) == {
            "from": "2026-09-01T00:00:00+00:00",
            "to": "2026-09-02T00:00:00.123000+00:00",
        }
        return web.json_response([])

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        await calculate(
            client,
            operation,
            from_timestamp=datetime(2026, 9, 1, tzinfo=UTC),
            to_timestamp=datetime(2026, 9, 2, microsecond=123000, tzinfo=UTC),
        )


@pytest.mark.parametrize("parameter", ["from_timestamp", "to_timestamp", "time_zone"])
async def test_filters_can_be_provided_individually(serve, operation, parameter):
    names = {"from_timestamp": "from", "to_timestamp": "to", "time_zone": "timeZone"}
    value = "Europe/Berlin" if parameter == "time_zone" else datetime(2026, 1, 1, tzinfo=UTC)

    async def handler(request):
        assert set(request.query) == {names[parameter]}
        return web.json_response([])

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        await calculate(client, operation, **{parameter: value})


class MissingOffset(tzinfo):
    def utcoffset(self, dt):
        return None


@pytest.mark.parametrize("parameter", ["from_timestamp", "to_timestamp"])
@pytest.mark.parametrize(
    "value", [datetime(2026, 1, 1), datetime(2026, 1, 1, tzinfo=MissingOffset())]
)
async def test_naive_dates_are_rejected_before_request(operation, parameter, value):
    client = EnergyTrackerClient("test-token")
    client._make_request = AsyncMock()
    with pytest.raises(ValidationError) as exc:
        await calculate(client, operation, **{parameter: value})
    assert exc.value.status_code is None
    client._make_request.assert_not_called()


async def test_date_outside_utc_range_is_local_validation_error(operation):
    client = EnergyTrackerClient("test-token")
    client._make_request = AsyncMock()
    with pytest.raises(ValidationError):
        await calculate(
            client, operation, from_timestamp=datetime(1, 1, 1, tzinfo=timezone(timedelta(hours=1)))
        )
    client._make_request.assert_not_called()


@pytest.mark.parametrize(
    "options", [{"interval": "minute"}, {"interval": "day", "method": "unknown"}]
)
async def test_invalid_path_enums_are_rejected_before_request(options):
    client = EnergyTrackerClient("test-token")
    client._make_request = AsyncMock()
    with pytest.raises(ValidationError):
        await client.calculations.extrapolations("device-id", **options)
    client._make_request.assert_not_called()


async def test_response_order_and_terminal_points_are_preserved(serve, operation):
    async def handler(request):
        return web.json_response(
            [
                {
                    "date": "2026-03-28T23:00:00Z",
                    "actualValue": 4.2,
                    "actualDuration": 82800,
                    "expectedValue": 8.4,
                    "expectedDuration": 86400,
                },
                {
                    "date": "2026-03-29T22:00:00Z",
                    "actualValue": 0,
                    "actualDuration": 0,
                    "expectedValue": 0,
                    "expectedDuration": 0,
                },
            ]
        )

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        points = await calculate(client, operation)
    assert [point.date for point in points] == [
        datetime(2026, 3, 28, 23, tzinfo=UTC),
        datetime(2026, 3, 29, 22, tzinfo=UTC),
    ]
    assert points[0].expected_value == 8.4
    assert points[0].actual_duration == 82800
    assert points[1].expected_duration == 0


@pytest.mark.parametrize("status", [201, 202, 204, 206, 302])
async def test_only_200_is_accepted(serve, operation, status):
    async def handler(request):
        return web.json_response([], status=status)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError, match="Unexpected HTTP status") as exc:
            await calculate(client, operation)
        assert exc.value.status_code == status


@pytest.mark.parametrize(
    "status,error",
    [
        (400, ValidationError),
        (401, AuthenticationError),
        (403, ForbiddenError),
        (404, ResourceNotFoundError),
        (409, ConflictError),
        (429, RateLimitError),
        (503, ServiceUnavailableError),
        (500, EnergyTrackerAPIError),
        (418, EnergyTrackerAPIError),
    ],
)
async def test_http_errors_preserve_status_and_do_not_retry(serve, operation, status, error):
    requests = 0

    async def handler(request):
        nonlocal requests
        requests += 1
        return web.json_response(
            {"message": "Calculation unavailable"}, status=status, headers={"Retry-After": "7"}
        )

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(error) as exc:
            await calculate(client, operation)
        assert type(exc.value) is error
        assert exc.value.status_code == status
        assert exc.value.api_message == ["Calculation unavailable"]
        assert isinstance(exc.value, EnergyTrackerAPIError)
        if status == 429:
            assert exc.value.retry_after == 7
    assert requests == 1


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [None],
        [{}],
        [
            {
                "date": "2026-01-01",
                "actualValue": 0,
                "actualDuration": 0,
                "expectedValue": 0,
                "expectedDuration": 0,
            }
        ],
    ],
)
async def test_invalid_response_shape_is_api_error(serve, operation, payload):
    async def handler(request):
        return web.json_response(payload)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError):
            await calculate(client, operation)


async def test_calculation_timeout_does_not_replace_session_timeout(serve, operation):
    async def handler(request):
        await asyncio.sleep(0.05)
        return web.json_response([])

    async with EnergyTrackerClient(
        "test-token", base_url=await serve(handler), timeout=0.01, calculation_timeout=1
    ) as client:
        session = await client._get_session()
        assert await calculate(client, operation) == []
        assert session is await client._get_session()
        assert session.timeout.total == 0.01
        with pytest.raises(TimeoutError):
            await client.devices.list_standard()


async def test_calculation_deadline_is_enforced_without_retries(serve, operation):
    requests = 0

    async def handler(request):
        nonlocal requests
        requests += 1
        await asyncio.sleep(0.05)
        return web.json_response([])

    async with EnergyTrackerClient(
        "test-token", base_url=await serve(handler), calculation_timeout=0.01
    ) as client:
        with pytest.raises(TimeoutError) as exc:
            await calculate(client, operation)
        assert exc.value.status_code is None
    assert requests == 1


def test_default_and_custom_timeouts():
    default = EnergyTrackerClient("test-token")
    assert default._timeout.total == 10
    assert default._calculation_timeout.total == 60
    configured = EnergyTrackerClient("test-token", None, 30, calculation_timeout=90)
    assert configured._timeout.total == 30
    assert configured._calculation_timeout.total == 90


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), True, None, "60"])
def test_invalid_calculation_timeout(value):
    with pytest.raises(ValueError, match="calculation_timeout"):
        EnergyTrackerClient("test-token", calculation_timeout=value)
