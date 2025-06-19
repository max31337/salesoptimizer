from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Union, Any
import json
import logging

from api.dependencies.auth import get_current_user_from_websocket_cookies
from domain.organization.entities.user import User
from infrastructure.websocket.websocket_manager import websocket_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/sla-monitoring")
async def sla_monitoring_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time SLA monitoring updates."""
    user = None
    
    try:
        logger.info("WebSocket connection attempt")
        
        # Authenticate user using cookies
        logger.info("Authenticating WebSocket using cookies...")
        user = await get_current_user_from_websocket_cookies(websocket)
        if not user:
            logger.warning("WebSocket authentication failed: invalid or missing token in cookies")
            await websocket.close(code=4001, reason="Invalid token")
            return
        if user.role.value != 'super_admin':
            logger.warning(f"WebSocket authentication failed: insufficient permissions for user {user.email}")
            await websocket.close(code=4001, reason="Unauthorized")
            return
        logger.info(f"WebSocket authenticated for user: {user.email}")
        
        # Connect the WebSocket
        user_id = str(user.id.value) if user.id else str(user.id)
        logger.info(f"Connecting WebSocket for user {user_id}")
        await websocket_manager.connect(websocket, user_id, "sla_monitoring")
          # Send initial data
        logger.info("Sending initial SLA data...")
        await send_current_sla_data(websocket, user)
        
        try:
            while True:
                # Keep the connection alive and handle any incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)
                logger.info(f"Received WebSocket message: {message.get('type')}")
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket_manager.send_to_websocket(websocket, {
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                elif message.get("type") == "request_update":
                    # Client is requesting immediate update
                    await send_current_sla_data(websocket, user)
                
        except WebSocketDisconnect:
            user_id = user.id.value if user.id else "unknown"
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            user_id = user.id.value if user.id else "unknown"
            logger.error(f"Error in WebSocket for user {user_id}: {e}")
        
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        try:
            await websocket.close(code=4001, reason="Authentication failed")
        except:
            pass  # Connection might already be closed
    finally:
        if user and user.id:
            await websocket_manager.disconnect(websocket, str(user.id.value))


async def send_current_sla_data(websocket: WebSocket, user: User):
    """Send current SLA data to a specific WebSocket connection."""
    try:
        from infrastructure.db.database import get_async_session
        from infrastructure.dependencies.service_container import get_sla_monitoring_use_case
        
        logger.info("🔄 Starting to send current SLA data...")
        
        # Get database session and SLA use case using async context manager
        async for session in get_async_session():
            sla_use_case = await get_sla_monitoring_use_case(session)
            
            system_health = await sla_use_case.get_system_health_summary()
            alerts = await sla_use_case.get_current_alerts()
            logger.info(f"📊 Retrieved system health: {system_health.overall_status if system_health else 'None'}")
            logger.info(f"🚨 Retrieved alerts count: {len(alerts) if alerts else 0}")
            
            # Send system health update with correct structure expected by frontend
            logger.info(f"📤 Sending SLA data via WebSocket - Status: {system_health.overall_status}, Health: {system_health.health_percentage}%")
            message_data: Dict[str, Any] = {
                "type": "sla_update",
                "data": {
                    "system_health": {
                        "overall_status": system_health.overall_status,
                        "health_percentage": system_health.health_percentage,
                        "uptime_status": system_health.uptime_status,
                        "uptime_percentage": system_health.uptime_percentage,
                        "uptime_duration": system_health.uptime_duration,
                        "system_start_time": getattr(system_health, 'system_start_time', None),
                        "last_updated": system_health.last_updated,
                        "total_metrics": system_health.total_metrics,
                        "healthy_metrics": system_health.healthy_metrics,
                        "warning_metrics": system_health.warning_metrics,
                        "critical_metrics": system_health.critical_metrics,
                        "metrics_summary": system_health.metrics_summary
                    },
                    "alerts": [
                        {
                            "id": alert.id,
                            "alert_type": alert.alert_type,
                            "title": alert.title,
                            "message": alert.message,
                            "metric_type": alert.metric_type,
                            "current_value": alert.current_value,
                            "threshold_value": alert.threshold_value,
                            "triggered_at": alert.triggered_at.isoformat(),
                            "acknowledged": alert.acknowledged
                        }
                        for alert in alerts
                    ],
                    "connection_info": {
                        "active_connections": websocket_manager.get_connection_count("sla_monitoring"),
                        "update_interval": 30000  # 30 seconds
                    }
                }
            }
            
            logger.info(f"📤 Sending WebSocket message with type: {message_data['type']}")
            await websocket_manager.send_to_websocket(websocket, message_data)
            logger.info("✅ Successfully sent SLA data via WebSocket")
            break  # Exit the async generator after first iteration
        
    except Exception as e:
        logger.error(f"❌ Error sending current SLA data: {e}", exc_info=True)


@router.get("/ws/sla-monitoring/status")
async def get_websocket_status() -> Dict[str, Union[int, str]]:
    """Get WebSocket connection status."""
    return {
        "active_connections": websocket_manager.get_connection_count("sla_monitoring"),
        "total_connections": websocket_manager.get_connection_count(),
        "service": "SLA Monitoring WebSocket",
        "status": "operational"
    }
