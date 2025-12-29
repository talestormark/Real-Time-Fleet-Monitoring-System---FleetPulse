from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime

from app.domain.models import Device
from app.domain.schemas import DeviceCreate, DeviceUpdate


class DeviceService:
    @staticmethod
    async def create_device(db: AsyncSession, device: DeviceCreate) -> Device:
        """Create a new device."""
        db_device = Device(**device.model_dump())
        db.add(db_device)
        await db.commit()
        await db.refresh(db_device)
        return db_device

    @staticmethod
    async def get_device(db: AsyncSession, device_id: str) -> Optional[Device]:
        """Get a device by ID."""
        result = await db.execute(select(Device).where(Device.id == device_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_devices(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        city: Optional[str] = None,
        status: Optional[str] = None,
        battery_lt: Optional[int] = None
    ) -> List[Device]:
        """Get all devices with optional filters."""
        query = select(Device)

        if city:
            query = query.where(Device.city == city)
        if status:
            query = query.where(Device.status == status)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_device(
        db: AsyncSession,
        device_id: str,
        device_update: DeviceUpdate
    ) -> Optional[Device]:
        """Update a device."""
        update_data = device_update.model_dump(exclude_unset=True)
        if not update_data:
            return await DeviceService.get_device(db, device_id)

        stmt = (
            update(Device)
            .where(Device.id == device_id)
            .values(**update_data)
            .returning(Device)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_device(db: AsyncSession, device_id: str) -> bool:
        """Delete a device."""
        stmt = delete(Device).where(Device.id == device_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def update_last_seen(db: AsyncSession, device_id: str, timestamp: datetime) -> None:
        """Update the last_seen_at timestamp for a device."""
        stmt = (
            update(Device)
            .where(Device.id == device_id)
            .values(last_seen_at=timestamp, status='online')
        )
        await db.execute(stmt)
        await db.commit()
