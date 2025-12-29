from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import redis.asyncio as redis

from app.api.deps import get_db
from app.domain.schemas import (
    TelemetryReadingCreate,
    TelemetryReadingResponse,
    IngestResponse
)
from app.services.telemetry_service import TelemetryService
from app.services.device_service import DeviceService
from app.core.config import settings

router = APIRouter()

# Redis client for pub/sub
redis_client = None


async def get_redis():
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


@router.post("/ingest", response_model=IngestResponse)
async def ingest_telemetry(
    reading: TelemetryReadingCreate,
    db: AsyncSession = Depends(get_db)
):
    """Ingest a single telemetry reading."""
    # Verify device exists
    device = await DeviceService.get_device(db, reading.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Create telemetry reading
    db_reading = await TelemetryService.create_reading(db, reading)

    # Update device last_seen
    await DeviceService.update_last_seen(db, reading.device_id, reading.ts)

    # Publish to Redis for real-time updates
    try:
        r = await get_redis()
        await r.publish("telemetry:new", f"{reading.device_id}")
    except Exception as e:
        print(f"Redis publish error: {e}")

    return IngestResponse(accepted=True, reading_id=db_reading.id)


@router.get("/devices/{device_id}/telemetry", response_model=List[TelemetryReadingResponse])
async def get_device_telemetry(
    device_id: str,
    from_ts: Optional[datetime] = Query(None, alias="from"),
    to_ts: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """Get telemetry readings for a specific device."""
    # Verify device exists
    device = await DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return await TelemetryService.get_device_telemetry(
        db, device_id, from_ts=from_ts, to_ts=to_ts, limit=limit
    )


@router.get("/devices/{device_id}/latest", response_model=Optional[TelemetryReadingResponse])
async def get_latest_telemetry(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the latest telemetry reading for a device."""
    device = await DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return await TelemetryService.get_latest_reading(db, device_id)
