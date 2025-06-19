from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum


class SLAStatus(Enum):
    """SLA status levels."""
    
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    
    def __str__(self) -> str:
        return self.value


class MetricType(Enum):
    """Types of metrics to monitor."""
    
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    ACTIVE_USERS = "active_users"
    DATABASE_CONNECTIONS = "database_connections"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_USAGE = "disk_usage"
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SLAThreshold:
    """SLA threshold configuration."""
    
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    unit: str  # e.g., "%", "ms", "count"
    
    def get_status(self, value: float) -> SLAStatus:
        """Determine SLA status based on value and thresholds."""
        if value >= self.critical_threshold:
            return SLAStatus.CRITICAL
        elif value >= self.warning_threshold:
            return SLAStatus.WARNING
        else:
            return SLAStatus.HEALTHY


@dataclass(frozen=True)
class SLAMetric:
    """Individual SLA metric measurement."""
    
    id: UUID
    metric_type: MetricType
    value: float
    threshold: SLAThreshold
    status: SLAStatus
    measured_at: datetime
    additional_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        metric_type: MetricType,
        value: float,
        threshold: SLAThreshold,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> "SLAMetric":
        """Create a new SLA metric with calculated status."""
        status = threshold.get_status(value)
        return cls(
            id=uuid4(),
            metric_type=metric_type,
            value=value,
            threshold=threshold,
            status=status,
            measured_at=datetime.now(timezone.utc),
            additional_data=additional_data or {}
        )
    
    @property
    def is_healthy(self) -> bool:
        """Check if metric is in healthy state."""
        return self.status == SLAStatus.HEALTHY
    
    @property
    def needs_attention(self) -> bool:
        """Check if metric needs attention (warning or critical)."""
        return self.status in [SLAStatus.WARNING, SLAStatus.CRITICAL]


@dataclass(frozen=True)
class SLAReport:
    """Complete SLA monitoring report."""
    
    id: UUID
    report_type: str  # e.g., "system_health", "performance", "availability"
    metrics: list[SLAMetric]
    overall_status: SLAStatus
    generated_at: datetime
    summary: str
    recommendations: list[str]
    additional_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        report_type: str,
        metrics: list[SLAMetric],
        summary: str,
        recommendations: list[str],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> "SLAReport":
        """Create a new SLA report with calculated overall status."""
        overall_status = cls._calculate_overall_status(metrics)
        return cls(
            id=uuid4(),
            report_type=report_type,
            metrics=metrics,
            overall_status=overall_status,
            generated_at=datetime.now(timezone.utc),
            summary=summary,
            recommendations=recommendations,
            additional_data=additional_data or {}
        )
    
    @staticmethod
    def _calculate_overall_status(metrics: list[SLAMetric]) -> SLAStatus:
        """Calculate overall status based on all metrics."""
        if not metrics:
            return SLAStatus.UNKNOWN
        
        # If any metric is critical, overall is critical
        if any(m.status == SLAStatus.CRITICAL for m in metrics):
            return SLAStatus.CRITICAL
        
        # If any metric is warning, overall is warning
        if any(m.status == SLAStatus.WARNING for m in metrics):
            return SLAStatus.WARNING
        
        # If all metrics are healthy, overall is healthy
        if all(m.status == SLAStatus.HEALTHY for m in metrics):
            return SLAStatus.HEALTHY
        
        return SLAStatus.UNKNOWN
    
    @property
    def critical_metrics(self) -> list[SLAMetric]:
        """Get all critical metrics."""
        return [m for m in self.metrics if m.status == SLAStatus.CRITICAL]
    
    @property
    def warning_metrics(self) -> list[SLAMetric]:
        """Get all warning metrics."""
        return [m for m in self.metrics if m.status == SLAStatus.WARNING]
    
    @property
    def healthy_metrics(self) -> list[SLAMetric]:
        """Get all healthy metrics."""
        return [m for m in self.metrics if m.status == SLAStatus.HEALTHY]
