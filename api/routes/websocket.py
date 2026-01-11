"""
WebSocket endpoint for real-time conversation updates.
Provides live conversation and message streaming without page reload.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Set, Dict
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Store active WebSocket connections
# Format: {room_id: set(websocket_connections)}
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        """Accept a WebSocket connection and add to room."""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        
        self.active_connections[room_id].add(websocket)
        logger.info(f"✓ WebSocket connected to room: {room_id} (total: {len(self.active_connections[room_id])})")
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        """Remove a WebSocket connection from room."""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            logger.info(f"✗ WebSocket disconnected from room: {room_id} (remaining: {len(self.active_connections[room_id])})")
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def broadcast_to_room(self, room_id: str, data: dict):
        """Send message to all connections in a room."""
        if room_id not in self.active_connections:
            return
        
        message = json.dumps({
            "type": "update",
            "timestamp": datetime.utcnow().isoformat(),
            **data
        })
        
        # Send to all connections in room
        disconnected = []
        for connection in self.active_connections[room_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, room_id)
    
    async def broadcast_to_all(self, data: dict):
        """Broadcast to all rooms."""
        message = json.dumps({
            "type": "update",
            "timestamp": datetime.utcnow().isoformat(),
            **data
        })
        
        for room_id in list(self.active_connections.keys()):
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.warning(f"Failed to send WebSocket message: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, room_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/conversations")
async def websocket_conversations(
    websocket: WebSocket,
    user_type: str = Query("admin")
):
    """
    WebSocket endpoint for real-time conversation updates.
    
    Room: conversations
    - Streams live conversation list updates
    - No polling needed - instant updates
    
    Query Parameters:
    - user_type: 'admin' (default) or 'support'
    """
    room_id = f"conversations_{user_type}"
    
    await manager.connect(websocket, room_id)
    
    try:
        while True:
            # Keep connection alive and receive heartbeats/pings
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    # Respond with pong to keep connection alive
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
                elif message.get("type") == "refresh":
                    # Client requests fresh data
                    await websocket.send_text(json.dumps({
                        "type": "refresh_request",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        logger.info(f"WebSocket disconnected gracefully from {room_id}")
    except Exception as e:
        logger.error(f"WebSocket error in {room_id}: {e}")
        manager.disconnect(websocket, room_id)


@router.websocket("/ws/conversation/{phone_number}")
async def websocket_conversation_detail(
    websocket: WebSocket,
    phone_number: str
):
    """
    WebSocket endpoint for real-time messages in a specific conversation.
    
    Room: conversation_{phone_number}
    - Streams new messages as they arrive
    - Updates message count
    - Shows typing indicators
    """
    room_id = f"conversation_{phone_number}"
    
    await manager.connect(websocket, room_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
                elif message.get("type") == "typing":
                    # Broadcast typing indicator
                    await manager.broadcast_to_room(room_id, {
                        "type": "typing",
                        "admin_name": message.get("admin_name", "Admin"),
                        "phone_number": phone_number
                    })
                
                elif message.get("type") == "stop_typing":
                    # Clear typing indicator
                    await manager.broadcast_to_room(room_id, {
                        "type": "stop_typing",
                        "phone_number": phone_number
                    })
            
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        logger.info(f"WebSocket disconnected from conversation {phone_number}")
    except Exception as e:
        logger.error(f"WebSocket error in conversation {phone_number}: {e}")
        manager.disconnect(websocket, room_id)


# Public broadcast function for other routes to use
async def broadcast_conversation_update(
    data: dict,
    user_type: str = "admin"
):
    """
    Broadcast conversation update to all connected clients.
    Called from conversation endpoints when data changes.
    
    Args:
        data: Update data to broadcast
        user_type: 'admin' or 'support'
    """
    room_id = f"conversations_{user_type}"
    await manager.broadcast_to_room(room_id, {
        "event": "conversation_updated",
        **data
    })


async def broadcast_message_update(
    phone_number: str,
    data: dict
):
    """
    Broadcast message update for a specific conversation.
    
    Args:
        phone_number: User's phone number
        data: Message data to broadcast
    """
    room_id = f"conversation_{phone_number}"
    await manager.broadcast_to_room(room_id, {
        "event": "message_received",
        **data
    })
