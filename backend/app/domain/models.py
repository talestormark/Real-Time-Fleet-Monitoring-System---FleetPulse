from sqlalchemy import Column, String, TIMESTAMP, Integer, Float, Text, CheckConstraint, Index, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    firmware_version = Column(Text)
    city = Column(Text)
    status = Column(
        Text,
        CheckConstraint("status IN ('online', 'offline', 'degraded')"),
        nullable=False,
        default='offline'
    )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_seen_at = Column(TIMESTAMP(timezone=True))
    device_metadata = Column(JSONB, default={})

    # Relationships
    telemetry_readings = relationship("TelemetryReading", back_populates="device", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="device", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_devices_city_status', 'city', 'status'),
        Index('idx_devices_last_seen', 'last_seen_at', postgresql_where=(status != 'offline')),
    )


class TelemetryReading(Base):
    __tablename__ = "telemetry_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Text, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    ts = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    battery_pct = Column(SmallInteger, CheckConstraint('battery_pct BETWEEN 0 AND 100'))
    speed_mps = Column(Float)
    temp_c = Column(Float)
    accel_g = Column(Float)

    # Relationship
    device = relationship("Device", back_populates="telemetry_readings")

    __table_args__ = (
        Index('idx_device_ts', 'device_id', 'ts'),
        Index('idx_ts_device', 'ts', 'device_id'),
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(Text, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    ts = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    type = Column(Text, nullable=False)  # LOW_BATTERY, STALE, IMPACT, GEOFENCE
    severity = Column(
        Text,
        CheckConstraint("severity IN ('info', 'warning', 'critical')"),
        nullable=False
    )
    payload = Column(JSONB, nullable=False, default={})
    acknowledged_at = Column(TIMESTAMP(timezone=True))
    acknowledged_by = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relationship
    device = relationship("Device", back_populates="events")

    __table_args__ = (
        Index('idx_events_device_ts', 'device_id', 'ts'),
        Index('idx_events_type_severity', 'type', 'severity', postgresql_where=(acknowledged_at.is_(None))),
        Index('idx_events_unacked', 'ts', postgresql_where=(acknowledged_at.is_(None))),
        Index(
            'idx_events_active',
            'device_id',
            'ts',
            postgresql_where=((acknowledged_at.is_(None)) & (severity.in_(['warning', 'critical'])))
        ),
    )
