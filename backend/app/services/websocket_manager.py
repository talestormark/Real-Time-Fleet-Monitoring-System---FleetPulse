from fastapi import WebSocket
from typing import Dict, Set, List
import json


class WebSocketManager:
    def __init__(self):
        # Store active connections by client_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store subscriptions: channel -> set of client_ids
        self.subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Remove client from all subscriptions
        for channel_subs in self.subscriptions.values():
            channel_subs.discard(client_id)

    async def subscribe(self, client_id: str, channels: List[str]):
        """Subscribe a client to channels."""
        for channel in channels:
            if channel not in self.subscriptions:
                self.subscriptions[channel] = set()
            self.subscriptions[channel].add(client_id)

    async def unsubscribe(self, client_id: str, channels: List[str]):
        """Unsubscribe a client from channels."""
        for channel in channels:
            if channel in self.subscriptions:
                self.subscriptions[channel].discard(client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)

    async def broadcast_to_channel(self, message: dict, channel: str):
        """Broadcast a message to all subscribers of a channel."""
        if channel in self.subscriptions:
            for client_id in self.subscriptions[channel]:
                await self.send_personal_message(message, client_id)

    async def broadcast_all(self, message: dict):
        """Broadcast a message to all connected clients."""
        for client_id in self.active_connections:
            await self.send_personal_message(message, client_id)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
