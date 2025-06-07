import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID

# Use TYPE_CHECKING for forward references
if TYPE_CHECKING:
    from infrastructure.db.models.user_model import UserModel


class ProfileUpdateRequestModel(Base):
    """Profile update request database model."""
    
    __tablename__ = "profile_update_requests"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    requested_by_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)    
    requested_changes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[user_id],
        back_populates="profile_update_requests"
    )

    requested_by: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[requested_by_id]
    )

    approved_by: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[approved_by_id]
    )
