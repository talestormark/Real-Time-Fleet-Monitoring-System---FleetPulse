from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager
import json
import uuid

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    client_id = str(uuid.uuid4())
    await ws_manager.connect(client_id, websocket)

    try:
        # Send connection confirmation
        await ws_manager.send_personal_message(
            {"type": "connected", "client_id": client_id},
            client_id
        )

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle subscription requests
            if message.get("type") == "subscribe":
                channels = message.get("channels", [])
                await ws_manager.subscribe(client_id, channels)
                await ws_manager.send_personal_message(
                    {"type": "subscribed", "channels": channels},
                    client_id
                )

            elif message.get("type") == "unsubscribe":
                channels = message.get("channels", [])
                await ws_manager.unsubscribe(client_id, channels)
                await ws_manager.send_personal_message(
                    {"type": "unsubscribed", "channels": channels},
                    client_id
                )

            elif message.get("type") == "ping":
                await ws_manager.send_personal_message(
                    {"type": "pong"},
                    client_id
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(client_id)
