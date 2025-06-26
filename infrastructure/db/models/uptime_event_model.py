import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID


class UptimeEventModel(Base):
    """Database model for uptime/downtime events."""
    
    __tablename__ = "uptime_events"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'start', 'end', 'downtime_start', 'downtime_end'
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # 'system', 'database', 'api', 'frontend'
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # For downtime events
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Reason for downtime
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default='minor')  # 'minor', 'major', 'critical'
    auto_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<UptimeEvent(id={self.id}, type={self.event_type}, service={self.service_name}, timestamp={self.timestamp})>"


class UptimeMetricModel(Base):
    """Database model for calculated uptime metrics."""
    
    __tablename__ = "uptime_metrics"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    uptime_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    total_downtime_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    downtime_incidents: Mapped[int] = mapped_column(nullable=False, default=0)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<UptimeMetric(id={self.id}, service={self.service_name}, uptime={self.uptime_percentage}%)>"
