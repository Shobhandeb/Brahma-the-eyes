from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        """Initializes the manager to hold all active frontend dashboard connections."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts a new WebSocket connection from the frontend."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Dashboard connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Removes a connection if the user closes their browser."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WebSocket] Dashboard disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast_alert(self, alert_data: dict):
        """
        Pushes a JSON alert payload to every single connected dashboard simultaneously.
        """
        # Create a copy of the list to iterate over, in case a connection drops during the loop
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(alert_data))
            except Exception as e:
                print(f"[WebSocket Error] Failed to send alert, dropping connection: {e}")
                self.disconnect(connection)

# We create a single global instance of this manager. 
# This ensures api.py and app.py are talking to the exact same list of connections.
ws_manager = ConnectionManager()