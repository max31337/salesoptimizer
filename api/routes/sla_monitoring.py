from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Annotated, Optional, Dict, Any
from datetime import datetime, timezone

from api.dependencies.auth import get_current_user_from_cookie
from domain.organization.entities.user import User
from application.use_cases.sla_monitoring_use_cases import SLAMonitoringUseCase
from application.dtos.monitoring_dto import (
    SLAReportResponse, SLASystemHealthResponse, SLAAlertResponse, SLAMetricResponse
)
from infrastructure.dependencies.service_container import get_sla_monitoring_use_case
from infrastructure.services.uptime_service_startup import get_uptime_status
from infrastructure.db.database import get_async_session
from infrastructure.services.uptime_monitoring_service import UptimeMonitoringService

router = APIRouter(prefix="/admin/sla", tags=["sla-monitoring"])


@router.get("/health", response_model=SLASystemHealthResponse)
async def get_system_health_summary(
    current_user: User = Depends(get_current_user_from_cookie),
    sla_use_case: SLAMonitoringUseCase = Depends(get_sla_monitoring_use_case)
):
    """Get system health summary (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    try:
        return await sla_use_case.get_system_health_summary()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health summary: {str(e)}"
        )


@router.get("/report", response_model=SLAReportResponse)
async def get_system_health_report(
    current_user: User = Depends(get_current_user_from_cookie),
    sla_use_case: SLAMonitoringUseCase = Depends(get_sla_monitoring_use_case)
):
    """Get comprehensive system health report (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    try:
        return await sla_use_case.get_system_health_report()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate system health report: {str(e)}"
        )


@router.get("/alerts", response_model=List[SLAAlertResponse])
async def get_current_alerts(
    current_user: User = Depends(get_current_user_from_cookie),
    sla_use_case: SLAMonitoringUseCase = Depends(get_sla_monitoring_use_case)
):
    """Get current active alerts (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    try:
        return await sla_use_case.get_current_alerts()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current alerts: {str(e)}"
        )


@router.get("/metrics", response_model=List[SLAMetricResponse])
async def get_metrics(
    metric_types: Annotated[Optional[List[str]], Query()] = None,
    current_user: User = Depends(get_current_user_from_cookie),
    sla_use_case: SLAMonitoringUseCase = Depends(get_sla_monitoring_use_case)
):
    """Get specific metrics by type (Super Admin only).
    
    Args:
        metric_types: List of metric types to collect (system, database, application)
    """
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    # Default to all metric types if none specified
    if not metric_types:
        metric_types = ["system", "database", "application"]
    
    # Validate metric types
    valid_types = ["system", "database", "application"]
    invalid_types = [t for t in metric_types if t not in valid_types]
    if invalid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metric types: {invalid_types}. Valid types are: {valid_types}"
        )
    
    try:
        return await sla_use_case.get_metrics_by_type(metric_types)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/status")
async def get_monitoring_status(
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Get SLA monitoring service status (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    return {
        "status": "operational",
        "service": "SLA Monitoring",
        "version": "1.0.0",
        "features": [
            "System Health Monitoring",
            "Performance Metrics Collection",
            "Real-time Alerts",
            "SLA Reporting"
        ],        "supported_metrics": [
            "Uptime",
            "CPU Usage",
            "Memory Usage", 
            "Disk Usage",
            "Database Response Time",
            "Active Users",
            "Database Connections"
        ]
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user_from_cookie),
    sla_use_case: SLAMonitoringUseCase = Depends(get_sla_monitoring_use_case)
) -> Dict[str, Any]:
    """Acknowledge an SLA alert (Super Admin and Org Admin only)."""
    # Check if current user is admin or super admin
    if current_user.role.value not in ['super_admin', 'org_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required to acknowledge alerts."
        )    
    try:
        # Get the current user ID
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required"
            )
        
        user_id_str = str(current_user.id.value)
        print(f"DEBUG: Acknowledging alert {alert_id} for user {user_id_str}")
        
        success = await sla_use_case.acknowledge_alert(alert_id, user_id_str)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found or already acknowledged"
            )
        
        # Trigger real-time update to all connected clients
        try:
            from infrastructure.services.sla_websocket_service import sla_websocket_service
            await sla_websocket_service.send_immediate_update()
        except Exception as e:
            # Don't fail the request if WebSocket update fails
            print(f"Warning: Failed to send WebSocket update: {e}")
        
        return {
            "success": True,
            "message": f"Alert {alert_id} acknowledged successfully",
            "acknowledged_by": current_user.email.value,
            "acknowledged_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.get("/uptime/summary")
async def get_uptime_summary(
    hours: int = Query(default=24, ge=1, le=168),  # 1 hour to 1 week
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Get detailed uptime summary for the specified period (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    try:
        from infrastructure.services.uptime_scheduler_service import get_uptime_scheduler
        scheduler = await get_uptime_scheduler()
        summary = await scheduler.get_uptime_summary(hours)
        
        return {
            "success": True,
            "data": summary,
            "period_hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get uptime summary: {str(e)}"
        )


@router.post("/uptime/health-check")
async def force_health_check(
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Force an immediate health check on all monitored services (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    try:
        from infrastructure.services.uptime_service_startup import force_health_check
        await force_health_check()
        
        return {
            "success": True,
            "message": "Health check completed successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform health check: {str(e)}"
        )


@router.get("/uptime/status")
async def get_uptime_monitoring_status(
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Get uptime monitoring service status (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    try:
        status_info = await get_uptime_status()
        
        return {
            "success": True,
            "data": status_info,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get uptime status: {str(e)}"
        )


@router.get("/uptime/incidents")
async def get_recent_incidents(
    hours: int = Query(default=24, ge=1, le=168),  # 1 hour to 1 week
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Get recent uptime incidents (Super Admin only)."""
    if current_user.role.value != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Super admin access required."
        )
    
    try:
        
        incidents = []
        async for session in get_async_session():
            uptime_service = UptimeMonitoringService(session)
            incidents = await uptime_service.get_recent_incidents(hours, limit)
            break
        
        return {
            "success": True,
            "data": incidents,
            "period_hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent incidents: {str(e)}"
        )
