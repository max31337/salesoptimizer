import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID

# Use TYPE_CHECKING for forward references
if TYPE_CHECKING:
    from infrastructure.db.models.user_model import UserModel
    from infrastructure.db.models.tenant_model import TenantModel


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    manager_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relationships using string references
    tenant: Mapped["TenantModel"] = relationship(
        "TenantModel", 
        foreign_keys=[tenant_id],
        back_populates="teams"
    )

    manager: Mapped["UserModel"] = relationship(
        "UserModel",
        primaryjoin="foreign(TeamModel.manager_id) == UserModel.id",
        back_populates="managed_teams",
        post_update=True
    )

    members: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        foreign_keys="UserModel.team_id",
        back_populates="team"
    )