from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.domain.models import Event
from app.domain.schemas import EventCreate


class EventService:
    @staticmethod
    async def create_event(db: AsyncSession, event: EventCreate) -> Event:
        """Create a new event."""
        db_event = Event(**event.model_dump())
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event

    @staticmethod
    async def get_event(db: AsyncSession, event_id: UUID) -> Optional[Event]:
        """Get an event by ID."""
        result = await db.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_events(
        db: AsyncSession,
        device_id: Optional[str] = None,
        severity: Optional[str] = None,
        type: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Get events with optional filters."""
        query = select(Event)

        if device_id:
            query = query.where(Event.device_id == device_id)
        if severity:
            query = query.where(Event.severity == severity)
        if type:
            query = query.where(Event.type == type)
        if acknowledged is not None:
            if acknowledged:
                query = query.where(Event.acknowledged_at.isnot(None))
            else:
                query = query.where(Event.acknowledged_at.is_(None))

        query = query.order_by(Event.ts.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def acknowledge_event(
        db: AsyncSession,
        event_id: UUID,
        acknowledged_by: str
    ) -> Optional[Event]:
        """Acknowledge an event."""
        stmt = (
            update(Event)
            .where(Event.id == event_id)
            .values(acknowledged_at=datetime.utcnow(), acknowledged_by=acknowledged_by)
            .returning(Event)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
