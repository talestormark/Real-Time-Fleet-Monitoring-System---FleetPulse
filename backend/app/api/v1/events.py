from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db
from app.domain.schemas import EventResponse, EventAcknowledge
from app.services.event_service import EventService

router = APIRouter()


@router.get("/", response_model=List[EventResponse])
async def list_events(
    device_id: Optional[str] = None,
    severity: Optional[str] = None,
    type: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List all events with optional filters."""
    return await EventService.get_events(
        db,
        device_id=device_id,
        severity=severity,
        type=type,
        acknowledged=acknowledged,
        skip=skip,
        limit=limit
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific event by ID."""
    event = await EventService.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/{event_id}/acknowledge", response_model=EventResponse)
async def acknowledge_event(
    event_id: UUID,
    ack_data: EventAcknowledge,
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an event."""
    event = await EventService.acknowledge_event(db, event_id, ack_data.acknowledged_by)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/devices/{device_id}/events", response_model=List[EventResponse])
async def get_device_events(
    device_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get events for a specific device."""
    return await EventService.get_events(
        db, device_id=device_id, skip=skip, limit=limit
    )
