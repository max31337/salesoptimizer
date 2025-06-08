from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as GUID
from datetime import datetime, timezone
import uuid
from typing import Dict, Any

from infrastructure.db.database import Base
from infrastructure.db.models.user_model import UserModel
from infrastructure.db.models.tenant_model import TenantModel

class ActivityLogModel(Base):
    """Activity log model for tracking user activities."""
    
    __tablename__ = "activity_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tenants.id"), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'user_login', 'user_created', 'team_joined', etc.
    activity_metadata: Mapped[Dict[str, Any]] = mapped_column(Text, nullable=True)  # JSON string for additional data
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="activity_logs")
    tenant: Mapped["TenantModel"] = relationship("TenantModel", back_populates="activity_logs")
