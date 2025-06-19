import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Boolean, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID


class SLAThresholdModel(Base):
    """Database model for SLA thresholds configuration."""
    
    __tablename__ = "sla_thresholds"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    critical_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    additional_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Ensure only one active threshold per metric type
    __table_args__ = (
        UniqueConstraint('metric_type', 'is_active', name='_metric_type_active_uc'),
    )

    def __repr__(self) -> str:
        return f"<SLAThreshold(id={self.id}, metric_type={self.metric_type}, warning={self.warning_threshold}, critical={self.critical_threshold})>"
