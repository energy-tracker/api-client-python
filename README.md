# Energy Tracker API Client

Python client for the Energy Tracker public REST API.

## Installation

```bash
pip install energy-tracker-api
```

## Requirements

- Python 3.10+
- Personal Access Token from Energy Tracker

## Usage

```python
from energy_tracker_api import EnergyTrackerClient, CreateMeterReadingDto
from datetime import datetime

client = EnergyTrackerClient(access_token="your-token")

meter_reading = CreateMeterReadingDto(
    value=123.45,
    timestamp=datetime.now(),     # Optional - server uses current time if omitted
    note="Manual reading"         # Optional
)

client.meter_readings.create(
    device_id="your-device-id",
    meter_reading=meter_reading,
    allow_rounding=True           # Optional
)
```

### Context Manager

```python
with EnergyTrackerClient(access_token="your-token") as client:
    reading = CreateMeterReadingDto(value=456.78)
    client.meter_readings.create("your-device-id", reading)
```

## Configuration

```python
client = EnergyTrackerClient(
    access_token="your-token",
    base_url="https://custom-api.example.com",  # Optional
    timeout=30                                  # Optional, default: 10 seconds
)
```

## Error Handling

```python
from energy_tracker_api import (
    EnergyTrackerAPIError,
    ValidationError,
    AuthenticationError,
    ForbiddenError,
    ResourceNotFoundError,
    ConflictError,
    RateLimitError
)

try:
    client.meter_readings.create(device_id, meter_reading)
except ValidationError as e:
    print(f"Validation error: {e}")
    print(f"Details: {e.api_message}")
except AuthenticationError:
    print("Authentication failed - check access token")
except ForbiddenError:
    print("Insufficient permissions")
except ResourceNotFoundError:
    print("No valid meter for timestamp")
except ConflictError:
    print("Meter reading already exists for timestamp")
except RateLimitError as e:
    print(f"Rate limit exceeded")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")
except EnergyTrackerAPIError as e:
    print(f"API error: {e}")
```

## API Reference

### EnergyTrackerClient

**`__init__(access_token, base_url=None, timeout=10)`**

- `access_token` (str): Personal Access Token
- `base_url` (str, optional): API base URL
- `timeout` (int, optional): Request timeout in seconds

### MeterReadingResource

**`meter_readings.create(device_id, meter_reading, allow_rounding=None)`**

Create a new meter reading.

- `device_id` (str): Device identifier
- `meter_reading` (CreateMeterReadingDto): Meter reading data
- `allow_rounding` (bool, optional): Allow rounding to meter precision

### CreateMeterReadingDto

**`CreateMeterReadingDto(value, timestamp=None, note=None)`**

- `value` (float): Meter reading value
- `timestamp` (datetime, optional): Reading timestamp (server uses current time if omitted)
- `note` (str, optional): Note for the meter reading

## Development

```bash
make install-dev  # Install dependencies
make test         # Run tests
make format       # Format code
make lint         # Run linters
```

## License

MIT
