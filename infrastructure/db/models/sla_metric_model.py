import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID


class SLAMetricModel(Base):
    """Database model for SLA metrics."""
    
    __tablename__ = "sla_metrics"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)    
    value: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold_warning: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_critical: Mapped[float] = mapped_column(Float, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    additional_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<SLAMetric(id={self.id}, type={self.metric_type}, value={self.value}, status={self.status})>"
