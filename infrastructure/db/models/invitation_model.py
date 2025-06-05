import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID

# Use TYPE_CHECKING for forward references
if TYPE_CHECKING:
    from infrastructure.db.models.user_model import UserModel
    from infrastructure.db.models.tenant_model import TenantModel


class InvitationModel(Base):    
    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    invited_by_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relationships using string references
    invited_by: Mapped["UserModel"] = relationship(
        "UserModel", 
        foreign_keys=[invited_by_id],
        back_populates="sent_invitations"
    )
    
    tenant: Mapped["TenantModel"] = relationship(
        "TenantModel", 
        foreign_keys=[tenant_id],
        back_populates="invitations"
    )