from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def broadcast_to_admins(self, message: dict):
        # This would need admin user IDs from database
        # For now, we'll just log
        print(f"Broadcast to admins: {message}")
    
    async def broadcast_to_role(self, message: dict, role: str):
        # In production, maintain list of admin connections
        pass

manager = ConnectionManager()
