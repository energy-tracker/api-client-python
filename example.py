"""Example usage of the Energy Tracker API client with error handling."""

from datetime import datetime
from energy_tracker_api import (
    EnergyTrackerClient,
    CreateMeterReadingDto,
    EnergyTrackerAPIError,
)

# Configuration - replace these values with your actual data
ACCESS_TOKEN = "your-personal-access-token-here"
DEVICE_ID = "deadbeef-dead-beef-dead-beefdeadbeef"


def submit_meter_reading(client: EnergyTrackerClient, value: float, note: str = None) -> None:
    """Submit a meter reading with comprehensive error handling.
    
    Args:
        client: The Energy Tracker API client.
        value: Meter reading value.
        note: Optional note for the reading.
    """
    reading = CreateMeterReadingDto(
        value=value,
        timestamp=datetime.now(),
        note=note
    )
    
    try:
        print(f"Submitting meter reading: {value}")
        client.meter_readings.create(
            device_id=DEVICE_ID,
            meter_reading=reading,
            keep_meter_precision=True
        )
        print("✓ Meter reading submitted successfully!")
        
    except EnergyTrackerAPIError as e:
        print(f"✗ Error: {e}")
        if e.api_message:
            for msg in e.api_message:
                print(f"  - {msg}")


def main():
    """Main example demonstrating error handling."""
    
    # Use client with context manager
    with EnergyTrackerClient(access_token=ACCESS_TOKEN) as client:
        # Example 1: Submit a simple meter reading
        submit_meter_reading(client, 123.45)
        
        # Example 2: Submit with note
        submit_meter_reading(
            client, 
            456.78, 
            note="Manual reading - basement electricity meter"
        )


if __name__ == "__main__":
    main()
