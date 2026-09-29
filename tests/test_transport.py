"""Regression tests using real HTTP responses from a local server."""

import asyncio
from datetime import datetime
from decimal import Decimal

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from energy_tracker_api import (
    CreateEnvironmentEntryDto,
    CreateEnvironmentRecordDto,
    CreateMeterReadingDto,
    EnergyTrackerAPIError,
    EnergyTrackerClient,
    ExportColumn,
    ExportMeterReadingsDto,
    RateLimitError,
    TimeoutError,
    ValidationError,
)


@pytest.fixture
async def serve():
    servers = []

    async def start(handler):
        app = web.Application()
        app.router.add_route("*", "/{path:.*}", handler)
        server = TestServer(app)
        servers.append(server)
        await server.start_server()
        return str(server.make_url("/"))

    yield start
    for server in servers:
        await server.close()


@pytest.mark.parametrize("body", [b'"123.45"', b'\xef\xbb\xbf"123.45"', b"123", b"null", b""])
async def test_export_preserves_exact_bytes(serve, body):
    async def handler(request):
        assert request.method == "POST"
        assert request.path == "/v3/devices/standard/device-id/meter-readings/export"
        return web.Response(body=body, content_type="text/csv", charset="utf-8")

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        result = await client.meter_readings.export(
            "device-id", ExportMeterReadingsDto(columns=[ExportColumn.VALUE], include_header=False)
        )
        assert result == body


@pytest.mark.parametrize(
    ("status", "error"),
    [(400, ValidationError), (429, RateLimitError), (503, EnergyTrackerAPIError)],
)
async def test_export_still_parses_json_errors(serve, status, error):
    async def handler(request):
        return web.json_response(
            {"message": ["Export unavailable"]}, status=status, headers={"Retry-After": "60"}
        )

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(error) as exc:
            await client.meter_readings.export(
                "device-id", ExportMeterReadingsDto(columns=[ExportColumn.VALUE])
            )
        assert exc.value.api_message == ["Export unavailable"]
        if status == 429:
            assert exc.value.retry_after == 60


async def test_non_json_error_keeps_http_error_type(serve):
    async def handler(request):
        return web.Response(text="<html>Unavailable</html>", content_type="text/html", status=503)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError, match="Server error: 503") as exc:
            await client.devices.list_standard()
        assert exc.value.api_message == []


@pytest.mark.parametrize(
    ("body", "content_type"),
    [
        (b"{", "application/json"),
        (b"\xff", "application/json"),
        (b"[]", "text/html"),
        (b"null", "application/json"),
        (b"42", "application/json"),
        (b"", "application/json"),
    ],
)
async def test_invalid_json_response_is_api_error(serve, body, content_type):
    async def handler(request):
        return web.Response(body=body, content_type=content_type)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError, match="Expected"):
            await client.devices.list_standard()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [None],
        [{}],
        [{"timestamp": "invalid", "value": "123", "rolloverOffset": 0, "meterId": "meter"}],
        [{"timestamp": None, "value": "123", "rolloverOffset": 0, "meterId": "meter"}],
        [
            {
                "timestamp": "2026-01-01T00:00:00Z",
                "value": "bad",
                "rolloverOffset": 0,
                "meterId": "meter",
            }
        ],
    ],
)
async def test_invalid_model_response_is_api_error(serve, payload):
    async def handler(request):
        return web.json_response(payload)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError):
            await client.meter_readings.list("device-id")


async def test_single_model_decode_error_preserves_cause(serve):
    async def handler(request):
        return web.json_response({"id": "environment-id"})

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError, match="Invalid EnvironmentRecordDto") as exc:
            await client.environments.get("device-id", "environment-id")
        assert isinstance(exc.value.__cause__, KeyError)


async def test_create_and_delete_accept_204(serve):
    calls = []
    timestamp = datetime.fromisoformat("2026-09-29T12:00:00Z")

    async def handler(request):
        assert request.headers["Authorization"] == "Bearer test-token"
        calls.append((request.method, await request.json()))
        return web.Response(status=204)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        assert (
            await client.meter_readings.create(
                "device-id", CreateMeterReadingDto(value=Decimal("1E+3"), timestamp=timestamp)
            )
            is None
        )
        assert await client.meter_readings.delete("device-id", timestamp) is None
    assert calls == [
        ("POST", {"value": "1000", "timestamp": "2026-09-29T12:00:00.000+00:00"}),
        ("DELETE", {"timestamp": "2026-09-29T12:00:00.000+00:00"}),
    ]


async def test_query_encoding_session_reuse_and_close(serve):
    async def handler(request):
        assert request.path == "/public-api/v1/devices/standard"
        assert request.headers["Authorization"] == "Bearer test-token"
        assert request.query["name"] == "Gas & Wasser"
        assert request.query["updatedAfter"] == "2026-09-29T12:00:00.000+02:00"
        return web.json_response([])

    async with EnergyTrackerClient(
        "test-token", base_url=await serve(handler) + "public-api/"
    ) as client:
        session = await client._get_session()
        for _ in range(2):
            assert (
                await client.devices.list_standard(
                    name="Gas & Wasser",
                    updated_after=datetime.fromisoformat("2026-09-29T12:00:00+02:00"),
                )
                == []
            )
            assert await client._get_session() is session
        assert not session.closed
    assert session.closed


@pytest.mark.parametrize(
    "timeout", [aiohttp.ClientTimeout(total=0.01), aiohttp.ClientTimeout(total=1, sock_read=0.01)]
)
async def test_real_timeouts_are_timeout_errors(serve, timeout):
    async def handler(request):
        await asyncio.sleep(0.1)
        return web.json_response([])

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(TimeoutError) as exc:
            await client._make_request("GET", "/slow", timeout=timeout)
        assert isinstance(exc.value.__cause__, asyncio.TimeoutError)


@pytest.mark.parametrize(
    ("resource", "method", "args", "expected_status", "payload"),
    [
        ("devices", "list_standard", (), 200, []),
        ("devices", "list_virtual", (), 200, []),
        ("meter_readings", "list", ("device",), 200, []),
        ("meter_readings", "create", ("device", CreateMeterReadingDto(Decimal("1"))), 204, None),
        (
            "meter_readings",
            "delete",
            ("device", datetime.fromisoformat("2026-09-29T12:00:00Z")),
            204,
            None,
        ),
        (
            "meter_readings",
            "export",
            ("device", ExportMeterReadingsDto(columns=[ExportColumn.VALUE])),
            200,
            "csv",
        ),
        ("environments", "list", ("device",), 200, []),
        (
            "environments",
            "get",
            ("device", "environment"),
            200,
            {"id": "environment", "title": "Temperature", "entries": []},
        ),
        (
            "environments",
            "create",
            ("device", CreateEnvironmentRecordDto("Temperature")),
            201,
            {"id": "environment", "title": "Temperature", "entries": []},
        ),
        ("environments", "delete", ("device", "environment"), 204, None),
        (
            "environments",
            "create_entry",
            ("device", "environment", CreateEnvironmentEntryDto(21.5)),
            204,
            None,
        ),
        (
            "environments",
            "delete_entry",
            ("device", "environment", datetime.fromisoformat("2026-09-29T12:00:00Z")),
            204,
            None,
        ),
    ],
)
@pytest.mark.parametrize("correct_status", [True, False])
async def test_each_endpoint_requires_its_exact_success_status(
    serve, resource, method, args, expected_status, payload, correct_status
):
    status = expected_status if correct_status else (201 if expected_status == 200 else 200)

    async def handler(request):
        if status == 204:
            return web.Response(status=status)
        if payload == "csv":
            return web.Response(text="123", content_type="text/csv", status=status)
        return web.json_response(payload, status=status)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        operation = getattr(getattr(client, resource), method)
        if correct_status:
            await operation(*args)
        else:
            with pytest.raises(
                EnergyTrackerAPIError,
                match=rf"Unexpected HTTP status: {status} \(expected {expected_status}\)",
            ):
                await operation(*args)


@pytest.mark.parametrize("status", [202, 204, 206, 304])
async def test_unexpected_status_is_rejected_before_decoding(serve, status):
    async def handler(request):
        return web.Response(status=status)

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError, match=f"Unexpected HTTP status: {status}"):
            await client.devices.list_standard()


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
async def test_redirect_is_rejected_without_following(serve, status):
    paths = []

    async def handler(request):
        paths.append(request.path)
        if request.path == "/redirect-target":
            return web.json_response([])
        return web.Response(status=status, headers={"Location": "/redirect-target"})

    async with EnergyTrackerClient("test-token", base_url=await serve(handler)) as client:
        with pytest.raises(EnergyTrackerAPIError, match=f"Unexpected HTTP status: {status}"):
            await client.devices.list_standard()
    assert paths == ["/v1/devices/standard"]
