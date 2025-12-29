from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.deps import get_db
from app.domain.schemas import DeviceCreate, DeviceUpdate, DeviceResponse
from app.services.device_service import DeviceService

router = APIRouter()


@router.post("", response_model=DeviceResponse, status_code=201)
async def create_device(
    device: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new device."""
    # Check if device already exists
    existing = await DeviceService.get_device(db, device.id)
    if existing:
        raise HTTPException(status_code=400, detail="Device already exists")

    return await DeviceService.create_device(db, device)


@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    city: Optional[str] = None,
    status: Optional[str] = None,
    battery_lt: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all devices with optional filters."""
    return await DeviceService.get_devices(
        db, skip=skip, limit=limit, city=city, status=status, battery_lt=battery_lt
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific device by ID."""
    device = await DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_update: DeviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a device."""
    device = await DeviceService.update_device(db, device_id, device_update)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a device."""
    deleted = await DeviceService.delete_device(db, device_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")
