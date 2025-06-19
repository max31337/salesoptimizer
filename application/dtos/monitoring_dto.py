from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class SLAMetricResponse(BaseModel):
    """SLA Metric response DTO."""
    
    id: str
    metric_type: str
    value: float
    status: str
    threshold_warning: float
    threshold_critical: float
    unit: str
    measured_at: datetime
    additional_data: Optional[Dict[str, Any]] = None


class SLAReportResponse(BaseModel):
    """SLA Report response DTO."""
    
    id: str
    report_type: str
    overall_status: str
    generated_at: datetime
    summary: str
    recommendations: List[str]
    metrics: List[SLAMetricResponse]
    additional_data: Optional[Dict[str, Any]] = None
    
    # Convenience properties
    critical_metrics_count: int
    warning_metrics_count: int
    healthy_metrics_count: int
    total_metrics_count: int


class SLASystemHealthResponse(BaseModel):
    """System health summary response DTO."""
    
    overall_status: str
    health_percentage: float
    uptime_status: str
    last_updated: datetime
    
    # Quick stats
    total_metrics: int
    healthy_metrics: int
    warning_metrics: int
    critical_metrics: int
    
    # Key metrics summary
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    database_response_time: Optional[float] = None
    active_users_24h: Optional[int] = None


class SLAAlertResponse(BaseModel):
    """SLA Alert response DTO."""
    
    id: str
    alert_type: str  # "critical", "warning", "info"
    title: str
    message: str
    metric_type: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
