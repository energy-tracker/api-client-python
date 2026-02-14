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

The client exposes three resource groups — all endpoints, parameters, and DTOs are documented in the [OpenAPI specification](https://github.com/energy-tracker/public-docs/blob/main/public-api/openapi.yml).

| Resource | Methods |
|---|---|
| `client.devices` | `list_standard()`, `list_virtual()` |
| `client.meter_readings` | `list()`, `create()`, `delete()`, `export()` |
| `client.environments` | `list()`, `get()`, `create()`, `delete()`, `create_entry()`, `delete_entry()` |

## Configuration

```python
client = EnergyTrackerClient(
    access_token="your-token",
    base_url="https://custom-api.example.com",  # Optional
    timeout=30,                                 # Optional, default: 10s
)
```

## Error Handling

All API errors inherit from `EnergyTrackerAPIError` and carry an `api_message` list with details from the server.

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
```

## License

MIT
