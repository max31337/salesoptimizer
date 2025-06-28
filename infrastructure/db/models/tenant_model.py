import uuid
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID

# Use TYPE_CHECKING for forward references
if TYPE_CHECKING:
    from infrastructure.db.models.user_model import UserModel
    from infrastructure.db.models.team_model import TeamModel
    from infrastructure.db.models.invitation_model import InvitationModel
    from infrastructure.db.models.activity_log_model import ActivityLogModel


class TenantModel(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    subscription_tier: Mapped[str] = mapped_column(String(50), nullable=False, default="basic")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=True)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    organization_size: Mapped[str] = mapped_column(String(50), nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships using string references (no imports needed)
    users: Mapped[list["UserModel"]] = relationship(
        "UserModel", 
        foreign_keys="UserModel.tenant_id",
        back_populates="tenant"
    )

    teams: Mapped[list["TeamModel"]] = relationship(
        "TeamModel", 
        foreign_keys="TeamModel.tenant_id",
        back_populates="tenant"
    )
    
    invitations: Mapped[list["InvitationModel"]] = relationship(
        "InvitationModel", 
        foreign_keys="InvitationModel.tenant_id",
        back_populates="tenant"
    )
    
    owner: Mapped["UserModel"] = relationship(
        "UserModel",
        primaryjoin="foreign(TenantModel.owner_id) == UserModel.id", 
        back_populates="owned_tenants",
        post_update=True
    )

    activity_logs: Mapped[list["ActivityLogModel"]] = relationship(
        "ActivityLogModel", 
        foreign_keys="ActivityLogModel.tenant_id",
        back_populates="tenant"
    )