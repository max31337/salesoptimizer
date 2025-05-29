import uuid
from datetime import datetime, timezone
from typing import Optional, Union, Any
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy import TypeDecorator, String as SqlString
from sqlalchemy.engine import Dialect
from infrastructure.db.base import Base


class GUID(TypeDecorator[uuid.UUID]):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36).
    Always returns uuid.UUID objects.
    """
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
        """Convert stored value back to UUID object."""
        if value is None:
            return None
        
        # Always return UUID objects for consistency
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError:
                raise ValueError(f"Invalid UUID string from database: {value}")
        return value


class UserModel(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID(), ForeignKey("tenants.id"), nullable=True)
    team_id = Column(GUID(), ForeignKey("teams.id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="sales_rep")
    status = Column(String(20), nullable=False, default="pending")
    is_email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    invitation_token = Column(String(255), nullable=True, index=True)
    invitation_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relationships with explicit primaryjoin
    tenant = relationship("TenantModel", back_populates="users")
    
    # User's team membership
    team = relationship(
        "TeamModel", 
        foreign_keys=[team_id], 
        back_populates="members"
    )
    
    # Teams managed by this user (no FK constraint, so we need primaryjoin)
    managed_teams = relationship(
        "TeamModel",
        primaryjoin="UserModel.id == TeamModel.manager_id",
        foreign_keys="TeamModel.manager_id",
        back_populates="manager",
        post_update=True
    )