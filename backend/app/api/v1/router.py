from fastapi import APIRouter
from app.api.v1 import devices, telemetry, events, websocket

api_router = APIRouter()

api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(telemetry.router, tags=["telemetry"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(websocket.router, tags=["websocket"])
