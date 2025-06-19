import json
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections by user ID
        self.connections: Dict[str, Set[WebSocket]] = {}
        # Store connections by subscription type
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, subscription_type: str = "sla_monitoring"):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.connections:
            self.connections[user_id] = set()
        self.connections[user_id].add(websocket)
        
        # Add to subscription connections
        if subscription_type not in self.subscriptions:
            self.subscriptions[subscription_type] = set()
        self.subscriptions[subscription_type].add(websocket)
        
        logger.info(f"WebSocket connected for user {user_id} with subscription {subscription_type}")
        
        # Send initial connection confirmation
        await self.send_to_websocket(websocket, {
            "type": "connection_established",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subscription_type": subscription_type,
            "message": "Real-time monitoring connected"
        })
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        # Remove from user connections
        if user_id in self.connections:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
        
        # Remove from all subscriptions
        for subscription_set in self.subscriptions.values():
            subscription_set.discard(websocket)
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_to_websocket(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send data to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {e}")
            # Connection might be closed, we'll handle cleanup in the endpoint
    
    async def send_to_user(self, user_id: str, data: Dict[str, Any]):
        """Send data to all WebSocket connections for a specific user."""
        if user_id in self.connections:
            disconnected: Set[WebSocket] = set()
            for websocket in self.connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(data))
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected:
                await self.disconnect(websocket, user_id)
    
    async def broadcast_to_subscription(self, subscription_type: str, data: Dict[str, Any]):
        """Broadcast data to all connections subscribed to a specific type."""
        if subscription_type in self.subscriptions:
            disconnected: Set[WebSocket] = set()
            connections = self.subscriptions[subscription_type].copy()
            
            for websocket in connections:
                try:
                    await websocket.send_text(json.dumps(data))
                except Exception as e:
                    logger.error(f"Error broadcasting to subscription {subscription_type}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected:
                self.subscriptions[subscription_type].discard(websocket)
    
    async def broadcast_sla_update(self, sla_data: Dict[str, Any]):
        """Broadcast SLA monitoring updates to all subscribed connections."""
        message: Dict[str, Any] = {
            "type": "sla_update",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": sla_data
        }
        await self.broadcast_to_subscription("sla_monitoring", message)
    
    async def broadcast_uptime_update(self, uptime_data: Dict[str, Any]):
        """Broadcast uptime updates to all subscribed connections."""
        message: Dict[str, Any] = {
            "type": "uptime_update",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": uptime_data
        }
        await self.broadcast_to_subscription("sla_monitoring", message)
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast new alerts to all subscribed connections."""
        message: Dict[str, Any] = {
            "type": "new_alert",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": alert_data
        }
        await self.broadcast_to_subscription("sla_monitoring", message)
    
    def get_connection_count(self, subscription_type: Optional[str] = None) -> int:
        """Get the number of active connections."""
        if subscription_type:
            return len(self.subscriptions.get(subscription_type, set()))
        return sum(len(connections) for connections in self.connections.values())


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
