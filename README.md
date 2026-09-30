# Energy Tracker API Client

Async Python client for the [Energy Tracker](https://github.com/energy-tracker) public REST API.

## Installation

```bash
pip install energy-tracker-api
```

## Requirements

- Python 3.14+
- Personal Access Token from Energy Tracker

## Quick Start

```python
import asyncio
from decimal import Decimal
from energy_tracker_api import EnergyTrackerClient, CreateMeterReadingDto

async def main():
    async with EnergyTrackerClient(access_token="your-token") as client:
        # List devices
        devices = await client.devices.list_standard()

        # Create a meter reading
        reading = CreateMeterReadingDto(value=Decimal("12345.67"))
        await client.meter_readings.create(
            device_id="your-device-id",
            meter_reading=reading,
        )

asyncio.run(main())
```

## Resources

The client exposes four resource groups — all endpoints, parameters, and DTOs are documented in the [OpenAPI specification](https://github.com/energy-tracker/public-docs/blob/main/public-api/openapi.yml).

| Resource | Methods |
|---|---|
| `client.devices` | `list_standard()`, `list_virtual()` |
| `client.meter_readings` | `list()`, `create()`, `delete()`, `export()` |
| `client.environments` | `list()`, `get()`, `create()`, `delete()`, `create_entry()`, `delete_entry()` |
| `client.calculations` | `daily_values()`, `extrapolations()` |

Starting with version 3.0.0, meter-reading CSV exports default to semicolon (`;`).
To preserve the comma-separated output of version 2.x, explicitly set
`delimiter=CsvDelimiter.COMMA` in `ExportMeterReadingsDto`.

## Configuration

```python
client = EnergyTrackerClient(
    access_token="your-token",
    base_url="https://custom-api.example.com",  # Optional
    timeout=30,                                 # Optional, default: 10s
    calculation_timeout=60,                     # Optional, calculations only
)
```

## Error Handling

All API errors inherit from `EnergyTrackerAPIError` and carry an `api_message` list with details from the server.
Each operation accepts only its documented success status (200, 201 or 204).
Unexpected statuses and redirects raise `EnergyTrackerAPIError`; redirects are not followed.

```python
from energy_tracker_api import (
    EnergyTrackerAPIError,
    ValidationError,
    AuthenticationError,
    ForbiddenError,
    ResourceNotFoundError,
    ConflictError,
    RateLimitError,
)

try:
    await client.meter_readings.create(device_id, reading)
except RateLimitError as e:
    print(f"Retry after {e.retry_after}s")
except EnergyTrackerAPIError as e:
    print(e.api_message)
```

## Development

```bash
make install-dev  # Install dependencies
make test         # Run tests
make type-check   # mypy
make format       # black + isort
make lint         # Linters
make check-dist   # Build, validate and import an isolated wheel installation
```

Package metadata, version and dependencies are maintained in `pyproject.toml`.
The requirements files are compatibility entry points for installing the package
and its development extra. The Makefile uses `python3.14` by default; override it
with `make install-dev PYTHON=/path/to/python3.14` when needed.

Meter reading values must be finite `Decimal` values. The client serializes them
as fixed-point strings without redundant fractional zeros and never rounds them.
Server-side range and precision validation still applies. When creating and
deleting the same reading, reuse its timestamp; prefer UTC-aware timestamps
with whole seconds as shown in `example.py`.

## License

MIT
