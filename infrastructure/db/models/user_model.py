import uuid
from datetime import datetime, timezone
from typing import Optional, Union, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import TypeDecorator, String as SqlString
from sqlalchemy.engine import Dialect

from infrastructure.db.database import Base

# Use TYPE_CHECKING for forward references
if TYPE_CHECKING:
    from infrastructure.db.models.tenant_model import TenantModel
    from infrastructure.db.models.team_model import TeamModel
    from infrastructure.db.models.invitation_model import InvitationModel
    from infrastructure.db.models.refresh_token_model import RefreshTokenModel
    from infrastructure.db.models.profile_update_request_model import ProfileUpdateRequestModel
    from infrastructure.db.models.activity_log_model import ActivityLogModel


class GUID(TypeDecorator[uuid.UUID]):
    """Platform-independent GUID type."""
    
    impl = SqlString
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Optional[Union[str, uuid.UUID]], dialect: Dialect) -> Optional[Union[str, uuid.UUID]]:
        """Convert incoming value for storage."""
        if value is None:
            return None
        
        # Ensure we have a UUID object
        if isinstance(value, str):
            try:
                uuid_obj = uuid.UUID(value)
            except ValueError:
                raise ValueError(f"Invalid UUID string: {value}")
        else:
            uuid_obj = value

        if dialect.name == 'postgresql':
            # PostgreSQL can handle UUID objects directly
            return uuid_obj
        else:
            # SQLite needs string representation
            return str(uuid_obj)

    def process_result_value(self, value: Optional[Union[str, uuid.UUID]], dialect: Dialect) -> Optional[uuid.UUID]:
        """Convert value from database to UUID object."""
        if value is None:
            return None
        
        if isinstance(value, str):
            return uuid.UUID(value)
        return value


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("tenants.id"), nullable=True)
    team_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("teams.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    profile_picture_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(String(1000), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="sales_rep")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    invitation_token: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    invitation_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=True)
    oauth_provider_id: Mapped[str] = mapped_column(String(255), nullable=True)    
    
    __table_args__ = (
        # Database-level constraints are handled by migration
        # See: infrastructure/db/alembic/versions/add_superadmin_constraint.py
    )

    # Relationships using string references (no imports needed)
    tenant: Mapped["TenantModel"] = relationship(
        "TenantModel", 
        foreign_keys=[tenant_id],
        back_populates="users"
    )

    # Tenants owned by this user (different relationship)
    owned_tenants: Mapped[list["TenantModel"]] = relationship(
        "TenantModel",
        primaryjoin="UserModel.id == foreign(TenantModel.owner_id)",
        back_populates="owner",
        post_update=True
    )

    team: Mapped["TeamModel"] = relationship(
        "TeamModel", 
        foreign_keys=[team_id], 
        back_populates="members"
    )

    # Teams managed by this user
    managed_teams: Mapped[list["TeamModel"]] = relationship(
        "TeamModel",
        primaryjoin="UserModel.id == foreign(TeamModel.manager_id)",
        back_populates="manager",
        post_update=True
    )
    
    # Invitations sent by this user
    sent_invitations: Mapped[list["InvitationModel"]] = relationship(
        "InvitationModel",
        foreign_keys="InvitationModel.invited_by_id",
        back_populates="invited_by"
    )

    # Refresh tokens relationship
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        "RefreshTokenModel",
        foreign_keys="RefreshTokenModel.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )    # Profile update requests relationship
    profile_update_requests: Mapped[list["ProfileUpdateRequestModel"]] = relationship(
        "ProfileUpdateRequestModel",
        foreign_keys="ProfileUpdateRequestModel.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Activity logs relationship
    activity_logs: Mapped[list["ActivityLogModel"]] = relationship(
        "ActivityLogModel",
        foreign_keys="ActivityLogModel.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )