from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import List

from app.domain.models import Device, TelemetryReading, Event
from app.domain.schemas import EventCreate
from app.core.config import settings
from app.services.event_service import EventService


class RulesEngine:
    """Engine for evaluating incident detection rules."""

    @staticmethod
    async def detect_low_battery(db: AsyncSession) -> List[EventCreate]:
        """Detect devices with low battery."""
        events = []

        # Get latest readings for each device using SQLAlchemy
        from sqlalchemy import select, func
        from sqlalchemy.sql import text

        # Use raw SQL with text() for distinct on
        query = text("""
        SELECT DISTINCT ON (device_id)
            device_id, battery_pct, ts
        FROM telemetry_readings
        WHERE battery_pct IS NOT NULL
        ORDER BY device_id, ts DESC
        """)

        result = await db.execute(query)
        readings = result.fetchall()

        for reading in readings:
            device_id, battery_pct, ts = reading
            if battery_pct < settings.LOW_BATTERY_THRESHOLD:
                # Check if event already exists (not acknowledged)
                existing = await db.execute(
                    select(Event).where(
                        Event.device_id == device_id,
                        Event.type == "LOW_BATTERY",
                        Event.acknowledged_at.is_(None)
                    ).limit(1)
                )
                if not existing.scalar_one_or_none():
                    events.append(EventCreate(
                        device_id=device_id,
                        type="LOW_BATTERY",
                        severity="warning" if battery_pct >= 10 else "critical",
                        payload={
                            "battery_pct": battery_pct,
                            "threshold": settings.LOW_BATTERY_THRESHOLD
                        }
                    ))

        return events

    @staticmethod
    async def detect_stale_devices(db: AsyncSession) -> List[EventCreate]:
        """Detect devices that haven't reported in a while."""
        events = []
        threshold_time = datetime.utcnow() - timedelta(
            minutes=settings.STALE_DEVICE_THRESHOLD_MINUTES
        )

        # Find devices with last_seen_at older than threshold
        query = select(Device).where(
            Device.last_seen_at < threshold_time,
            Device.status != 'offline'
        )
        result = await db.execute(query)
        devices = result.scalars().all()

        for device in devices:
            # Check if event already exists (not acknowledged)
            existing = await db.execute(
                select(Event).where(
                    Event.device_id == device.id,
                    Event.type == "STALE",
                    Event.acknowledged_at.is_(None)
                ).limit(1)
            )
            if not existing.scalar_one_or_none():
                minutes_ago = int((datetime.utcnow() - device.last_seen_at).total_seconds() / 60)
                events.append(EventCreate(
                    device_id=device.id,
                    type="STALE",
                    severity="warning",
                    payload={
                        "last_seen_mins_ago": minutes_ago,
                        "threshold_mins": settings.STALE_DEVICE_THRESHOLD_MINUTES
                    }
                ))

        return events

    @staticmethod
    async def detect_impacts(db: AsyncSession) -> List[EventCreate]:
        """Detect impact events based on accelerometer readings."""
        events = []

        # Look for recent high acceleration events
        since_time = datetime.utcnow() - timedelta(minutes=5)

        query = select(TelemetryReading).where(
            TelemetryReading.ts >= since_time,
            TelemetryReading.accel_g >= settings.IMPACT_THRESHOLD_G
        )
        result = await db.execute(query)
        readings = result.scalars().all()

        for reading in readings:
            # Check if event already exists for this timestamp
            existing = await db.execute(
                select(Event).where(
                    Event.device_id == reading.device_id,
                    Event.type == "IMPACT",
                    Event.ts == reading.ts
                ).limit(1)
            )
            if not existing.scalar_one_or_none():
                events.append(EventCreate(
                    device_id=reading.device_id,
                    type="IMPACT",
                    severity="critical",
                    payload={
                        "accel_g": reading.accel_g,
                        "lat": reading.lat,
                        "lon": reading.lon,
                        "ts": reading.ts.isoformat()
                    }
                ))

        return events

    @staticmethod
    async def evaluate_all_rules(db: AsyncSession) -> int:
        """Evaluate all rules and create events."""
        all_events = []

        # Run all detection rules
        all_events.extend(await RulesEngine.detect_low_battery(db))
        all_events.extend(await RulesEngine.detect_stale_devices(db))
        all_events.extend(await RulesEngine.detect_impacts(db))

        # Create events
        for event_data in all_events:
            await EventService.create_event(db, event_data)

        return len(all_events)
