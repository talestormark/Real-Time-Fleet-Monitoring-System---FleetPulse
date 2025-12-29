from app.worker.celery_app import celery_app
from app.services.rules_engine import RulesEngine
from app.services.websocket_manager import ws_manager
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.domain.models import Device
from app.core.config import settings
from datetime import datetime, timedelta
import asyncio


def get_async_session():
    """Create a new async session for each task to avoid event loop issues."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    return async_session, engine


@celery_app.task(name="app.worker.tasks.detect_incidents")
def detect_incidents():
    """Periodic task to detect incidents."""

    async def run():
        session_maker, engine = get_async_session()
        async with session_maker() as db:
            try:
                events_created = await RulesEngine.evaluate_all_rules(db)
                print(f"Incident detection completed. Created {events_created} events.")

                # Broadcast to WebSocket clients
                if events_created > 0:
                    await ws_manager.broadcast_to_channel(
                        {"type": "events_updated", "count": events_created},
                        "events"
                    )
            except Exception as e:
                print(f"Error in incident detection: {e}")
            finally:
                await engine.dispose()

    asyncio.run(run())


@celery_app.task(name="app.worker.tasks.update_device_status")
def update_device_status():
    """Update device online/offline status based on last_seen_at."""

    async def run():
        session_maker, engine = get_async_session()
        async with session_maker() as db:
            try:
                threshold_time = datetime.utcnow() - timedelta(
                    minutes=15  # Consider device offline after 15 minutes
                )

                # Update devices to offline if they haven't been seen recently
                stmt = (
                    update(Device)
                    .where(
                        Device.last_seen_at < threshold_time,
                        Device.status != 'offline'
                    )
                    .values(status='offline')
                )
                result = await db.execute(stmt)
                await db.commit()

                if result.rowcount > 0:
                    print(f"Updated {result.rowcount} devices to offline status.")
                    await ws_manager.broadcast_to_channel(
                        {"type": "device_status_updated"},
                        "devices"
                    )
            except Exception as e:
                print(f"Error updating device status: {e}")
            finally:
                await engine.dispose()

    asyncio.run(run())
