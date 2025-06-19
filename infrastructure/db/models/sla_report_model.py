import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID


class SLAReportModel(Base):
    """Database model for SLA reports."""
    
    __tablename__ = "sla_reports"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    overall_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    metrics_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)  # Snapshot of metrics at report time
    critical_metrics_count: Mapped[int] = mapped_column(nullable=False, default=0)
    warning_metrics_count: Mapped[int] = mapped_column(nullable=False, default=0)
    healthy_metrics_count: Mapped[int] = mapped_column(nullable=False, default=0)
    total_metrics_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    additional_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<SLAReport(id={self.id}, type={self.report_type}, status={self.overall_status}, generated_at={self.generated_at})>"
