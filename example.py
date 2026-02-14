"""Example usage of the Energy Tracker API client."""

import asyncio
from datetime import datetime
from decimal import Decimal

from energy_tracker_api import (
    CreateEnvironmentEntryDto,
    CreateEnvironmentRecordDto,
    CreateMeterReadingDto,
    EnergyTrackerAPIError,
    EnergyTrackerClient,
    ExportColumn,
    ExportMeterReadingsDto,
    RateLimitError,
    SortDirection,
)

ACCESS_TOKEN = "your-personal-access-token-here"
DEVICE_ID = "deadbeef-dead-beef-dead-beefdeadbeef"


async def main() -> None:
    async with EnergyTrackerClient(access_token=ACCESS_TOKEN) as client:

        # ── Devices ──────────────────────────────────────────────
        devices = await client.devices.list_standard()
        for d in devices:
            print(f"{d.name}  (id={d.id}, folder={d.folder_path})")

        virtual = await client.devices.list_virtual()
        print(f"{len(virtual)} virtual device(s)")

        # ── Meter Readings ───────────────────────────────────────
        # Create (returns None)
        reading = CreateMeterReadingDto(
            value=Decimal("12345.67"),
            timestamp=datetime.now(),
            note="Manual reading",
        )
        await client.meter_readings.create(
            device_id=DEVICE_ID,
            meter_reading=reading,
            allow_rounding=True,
        )
        print("Meter reading created")

        # List
        readings = await client.meter_readings.list(
            device_id=DEVICE_ID,
            sort=SortDirection.DESC,
        )
        for r in readings:
            print(f"  {r.timestamp}  {r.value}")

        # Export as CSV bytes
        export_config = ExportMeterReadingsDto(
            columns=[
                ExportColumn.DATE,
                ExportColumn.VALUE,
                ExportColumn.NOTE,
            ],
        )
        csv_bytes = await client.meter_readings.export(
            device_id=DEVICE_ID,
            export_config=export_config,
        )
        print(f"Exported {len(csv_bytes)} bytes")

        # Delete (returns None)
        await client.meter_readings.delete(
            device_id=DEVICE_ID,
            timestamp=datetime.now(),
        )
        print("Meter reading deleted")

        # ── Environments ─────────────────────────────────────────
        # Create a record (returns EnvironmentRecordDto)
        record = await client.environments.create(
            device_id=DEVICE_ID,
            environment_record=CreateEnvironmentRecordDto(
                title="Temperature", 
                unit="°C",
            ),
        )
        print(f"Created environment record: {record.title} (id={record.id})")

        # Add an entry (returns None)
        await client.environments.create_entry(
            device_id=DEVICE_ID,
            environment_id=record.id,
            entry=CreateEnvironmentEntryDto(value=21.5),
        )
        print("Environment entry created")

        # Clean up (both return None)
        await client.environments.delete_entry(
            device_id=DEVICE_ID,
            environment_id=record.id,
            timestamp=datetime.now(),
        )
        await client.environments.delete(
            device_id=DEVICE_ID,
            environment_id=record.id,
        )

        # ── Error handling ───────────────────────────────────────
        try:
            await client.meter_readings.create(
                device_id="non-existent", 
                meter_reading=reading,
            )
        except RateLimitError as e:
            print(f"Rate limited – retry after {e.retry_after}s")
        except EnergyTrackerAPIError as e:
            print(f"API error: {e}")
            for msg in e.api_message:
                print(f"  - {msg}")


if __name__ == "__main__":
    asyncio.run(main())
