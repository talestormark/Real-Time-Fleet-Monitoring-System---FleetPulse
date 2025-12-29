from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from app.domain.models import TelemetryReading
from app.domain.schemas import TelemetryReadingCreate


class TelemetryService:
    @staticmethod
    async def create_reading(
        db: AsyncSession,
        reading: TelemetryReadingCreate
    ) -> TelemetryReading:
        """Create a new telemetry reading."""
        db_reading = TelemetryReading(**reading.model_dump())
        db.add(db_reading)
        await db.commit()
        await db.refresh(db_reading)
        return db_reading

    @staticmethod
    async def get_device_telemetry(
        db: AsyncSession,
        device_id: str,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[TelemetryReading]:
        """Get telemetry readings for a device."""
        query = select(TelemetryReading).where(TelemetryReading.device_id == device_id)

        if from_ts:
            query = query.where(TelemetryReading.ts >= from_ts)
        if to_ts:
            query = query.where(TelemetryReading.ts <= to_ts)

        query = query.order_by(TelemetryReading.ts.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_latest_reading(
        db: AsyncSession,
        device_id: str
    ) -> Optional[TelemetryReading]:
        """Get the latest telemetry reading for a device."""
        query = (
            select(TelemetryReading)
            .where(TelemetryReading.device_id == device_id)
            .order_by(TelemetryReading.ts.desc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
