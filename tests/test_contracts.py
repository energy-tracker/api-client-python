"""Run the shared SDK contracts through the public Python API and a local HTTP server."""

import base64
import json
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from aiohttp import web
from jsonschema import Draft202012Validator

from energy_tracker_api import (
    AuthenticationError,
    CalculationInterval,
    ConflictError,
    CreateEnvironmentEntryDto,
    CreateEnvironmentRecordDto,
    CreateMeterReadingDto,
    CsvDelimiter,
    DateFormat,
    EnergyTrackerAPIError,
    EnergyTrackerClient,
    ExportColumn,
    ExportMeterReadingsDto,
    ExtrapolationMethod,
    ForbiddenError,
    RateLimitError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    SortDirection,
    ValidationError,
)

CONTRACTS = Path(__file__).resolve().parents[1] / "contracts"
ERRORS = {
    "validation": ValidationError,
    "authentication": AuthenticationError,
    "forbidden": ForbiddenError,
    "notFound": ResourceNotFoundError,
    "conflict": ConflictError,
    "rateLimit": RateLimitError,
    "unavailable": ServiceUnavailableError,
    "api": EnergyTrackerAPIError,
}
OPERATIONS = {
    "devices.listStandard": ("devices", "list_standard"),
    "devices.listVirtual": ("devices", "list_virtual"),
    "meterReadings.list": ("meter_readings", "list"),
    "meterReadings.create": ("meter_readings", "create"),
    "meterReadings.delete": ("meter_readings", "delete"),
    "meterReadings.export": ("meter_readings", "export"),
    "environments.list": ("environments", "list"),
    "environments.get": ("environments", "get"),
    "environments.create": ("environments", "create"),
    "environments.delete": ("environments", "delete"),
    "environments.createEntry": ("environments", "create_entry"),
    "environments.deleteEntry": ("environments", "delete_entry"),
    "calculations.dailyValues": ("calculations", "daily_values"),
    "calculations.extrapolations": ("calculations", "extrapolations"),
    "token.status": ("token", "status"),
}
TIMESTAMPS = {
    "timestamp",
    "date",
    "lastUpdatedAt",
    "expiresAt",
    "from",
    "to",
    "updatedAfter",
    "updatedBefore",
}


def load_cases():
    schema = json.loads((CONTRACTS / "schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    cases = []
    for path in sorted((CONTRACTS / "cases").glob("*.json")):
        suite = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(suite)
        cases.extend(suite["cases"])
    assert cases, "No contract cases found"
    assert len({case["id"] for case in cases}) == len(cases), "Duplicate contract case ID"
    assert {case["operation"] for case in cases} == set(OPERATIONS)
    return cases


CASES = load_cases()


def snake_case(name):
    return "".join("_" + char.lower() if char.isupper() else char for char in name)


def camel_case(name):
    first, *rest = name.split("_")
    return first + "".join(part.capitalize() for part in rest)


def arguments(data):
    """Adapt neutral fixture inputs to Python's public parameter and DTO types."""
    result = {}
    for key, value in data.items():
        name = snake_case(key)
        if key in TIMESTAMPS:
            value = datetime.fromisoformat(value)
            name = {"from": "from_timestamp", "to": "to_timestamp"}.get(key, name)
        elif key == "reading":
            value = CreateMeterReadingDto(**arguments(value))
            name = "meter_reading"
        elif key == "record":
            value = CreateEnvironmentRecordDto(**arguments(value))
            name = "environment_record"
        elif key == "entry":
            value = CreateEnvironmentEntryDto(**arguments(value))
        elif key == "config":
            value = ExportMeterReadingsDto(**arguments(value))
            name = "export_config"
        elif key == "value" and isinstance(value, str):
            value = Decimal(value)
        elif key == "columns":
            value = [ExportColumn(column) for column in value]
        elif key in {"sort", "interval", "method", "delimiter", "dateFormat"}:
            enum = {
                "sort": SortDirection,
                "interval": CalculationInterval,
                "method": ExtrapolationMethod,
                "delimiter": CsvDelimiter,
                "dateFormat": DateFormat,
            }[key]
            value = enum(value)
        result[name] = value
    return result


def normalize(value, key=None):
    """Expose native DTO results as neutral values; compare timestamps as instants."""
    if is_dataclass(value):
        return normalize(
            {camel_case(field.name): getattr(value, field.name) for field in fields(value)}
        )
    if isinstance(value, dict):
        return {name: normalize(item, name) for name, item in value.items()}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, bytes):
        return {"base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bool):
        # Python otherwise considers False == 0 and True == 1, unlike JSON.
        return ("boolean", value)
    if key in TIMESTAMPS and isinstance(value, str):
        value = datetime.fromisoformat(value)
    if isinstance(value, datetime):
        assert value.utcoffset() is not None, "Contract timestamp must have a UTC offset"
        return value.astimezone(UTC).isoformat()
    return value


def body_bytes(body):
    if "json" in body:
        return json.dumps(body["json"], ensure_ascii=False, allow_nan=False).encode("utf-8")
    if "base64" in body:
        return base64.b64decode(body["base64"], validate=True)
    return body.get("text", "").encode("utf-8")


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
async def test_api_contract(serve, case):
    requests = []

    async def handler(request):
        requests.append((request, await request.read()))
        response = case["response"]
        return web.Response(
            status=response["status"],
            headers=response["headers"],
            body=body_bytes(response["body"]),
        )

    # A base URL with a path also verifies that SDKs preserve reverse-proxy prefixes.
    async with EnergyTrackerClient(
        "contract-test-token", base_url=await serve(handler) + "public-api/"
    ) as client:
        resource, method = OPERATIONS[case["operation"]]
        operation = getattr(getattr(client, resource), method)
        kwargs = arguments(case["input"])
        expected = case["expected"]
        if "error" in expected:
            error = expected["error"]
            with pytest.raises(ERRORS[error["kind"]]) as caught:
                await operation(**kwargs)
            assert type(caught.value) is ERRORS[error["kind"]]
            assert caught.value.status_code == error["status"]
            assert caught.value.api_message == error["messages"]
            if "retryAfter" in error:
                assert caught.value.retry_after == error["retryAfter"]
        else:
            result = await operation(**kwargs)
            assert normalize(result) == normalize(expected["result"])

    # Assert outside the handler so a request mismatch cannot masquerade as an HTTP 500.
    assert len(requests) == 1, "Contract calls must not retry or follow redirects"
    request, raw_body = requests[0]
    expected_request = case["request"]
    assert request.method == expected_request["method"]
    assert request.path == "/public-api" + expected_request["path"]
    assert len(request.query) == len(expected_request["query"])
    assert normalize(dict(request.query)) == normalize(expected_request["query"])
    for name, value in expected_request["headers"].items():
        assert request.headers[name] == value
    if "json" in expected_request["body"]:
        assert normalize(json.loads(raw_body)) == normalize(expected_request["body"]["json"])
    else:
        assert raw_body == body_bytes(expected_request["body"])


def test_each_operation_has_success_and_wrong_status_cases():
    for operation in OPERATIONS:
        cases = [case for case in CASES if case["operation"] == operation]
        success_statuses = {
            case["response"]["status"] for case in cases if "result" in case["expected"]
        }
        assert len(success_statuses) == 1, operation
        assert any(
            "error" in case["expected"]
            and 200 <= case["response"]["status"] < 300
            and case["response"]["status"] not in success_statuses
            for case in cases
        ), operation
