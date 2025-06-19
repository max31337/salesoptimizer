import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID

if TYPE_CHECKING:
    from infrastructure.db.models.user_model import UserModel


class SLAAlertModel(Base):
    """Database model for SLA alerts."""
    
    __tablename__ = "sla_alerts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # warning, critical
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    current_value: Mapped[float] = mapped_column(nullable=False)
    threshold_value: Mapped[float] = mapped_column(nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    additional_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    acknowledged_by_user: Mapped[Optional["UserModel"]] = relationship("UserModel", foreign_keys=[acknowledged_by])

    def __repr__(self) -> str:
        return f"<SLAAlert(id={self.id}, type={self.alert_type}, metric={self.metric_type}, acknowledged={self.acknowledged})>"
