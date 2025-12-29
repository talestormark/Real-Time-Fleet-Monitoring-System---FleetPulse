from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# Device Schemas
class DeviceBase(BaseModel):
    name: str
    model: str
    firmware_version: Optional[str] = None
    city: Optional[str] = None


class DeviceCreate(DeviceBase):
    id: str


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = None


class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    created_at: datetime
    last_seen_at: Optional[datetime] = None
    device_metadata: Dict[str, Any] = {}


# Telemetry Schemas
class TelemetryReadingCreate(BaseModel):
    device_id: str
    ts: datetime
    lat: Optional[float] = None
    lon: Optional[float] = None
    battery_pct: Optional[int] = Field(None, ge=0, le=100)
    speed_mps: Optional[float] = None
    temp_c: Optional[float] = None
    accel_g: Optional[float] = None


class TelemetryReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    ts: datetime
    lat: Optional[float] = None
    lon: Optional[float] = None
    battery_pct: Optional[int] = None
    speed_mps: Optional[float] = None
    temp_c: Optional[float] = None
    accel_g: Optional[float] = None


class IngestResponse(BaseModel):
    accepted: bool
    reading_id: Optional[int] = None


# Event Schemas
class EventCreate(BaseModel):
    device_id: str
    type: str
    severity: str
    payload: Dict[str, Any] = {}


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: str
    ts: datetime
    type: str
    severity: str
    payload: Dict[str, Any]
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    created_at: datetime


class EventAcknowledge(BaseModel):
    acknowledged_by: str


# WebSocket Message Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None


class WebSocketSubscribe(BaseModel):
    type: str = "subscribe"
    channels: list[str]
