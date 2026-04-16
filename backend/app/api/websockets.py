from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.core.websocket import manager
import json

router = APIRouter(prefix="/ws", tags=["WebSockets"])

@router.websocket("/track/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    Connect a user to the websocket room to send/receive live tracking coordinates.
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receive text from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # If the user sends coordinates, we broadcast them to their contacts/admins
                if message.get("type") == "location_update":
                    # Broadcast to admins for demo purposes
                    await manager.broadcast_to_admins(message)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
