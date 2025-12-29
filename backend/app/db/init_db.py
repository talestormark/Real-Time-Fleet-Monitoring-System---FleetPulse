"""
Database initialization and seeding script.
Run this to populate the database with sample devices.
"""

import asyncio
from app.db.base import async_session_maker, engine, Base
from app.domain.models import Device
from datetime import datetime


async def init_db():
    """Initialize database with sample data."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed sample devices
    async with async_session_maker() as session:
        # Check if devices already exist
        from sqlalchemy import select
        result = await session.execute(select(Device).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded.")
            return

        sample_devices = [
            Device(
                id="bike-001",
                name="E-Bike Downtown 001",
                model="Urban Cruiser v2",
                firmware_version="2.1.0",
                city="New York",
                status="offline"
            ),
            Device(
                id="bike-002",
                name="E-Bike Midtown 002",
                model="Urban Cruiser v2",
                firmware_version="2.1.0",
                city="New York",
                status="offline"
            ),
            Device(
                id="bike-003",
                name="E-Bike Brooklyn 003",
                model="City Glide Pro",
                firmware_version="1.5.3",
                city="New York",
                status="offline"
            ),
            Device(
                id="scooter-001",
                name="Scooter SF 001",
                model="ZipZap X1",
                firmware_version="3.0.1",
                city="San Francisco",
                status="offline"
            ),
            Device(
                id="scooter-002",
                name="Scooter SF 002",
                model="ZipZap X1",
                firmware_version="3.0.1",
                city="San Francisco",
                status="offline"
            ),
        ]

        session.add_all(sample_devices)
        await session.commit()
        print(f"Seeded {len(sample_devices)} sample devices.")


if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(init_db())
    print("Database initialization complete.")
