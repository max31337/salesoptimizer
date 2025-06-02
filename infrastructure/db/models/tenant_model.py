import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship

from infrastructure.db.database import Base
from infrastructure.db.models.user_model import GUID


class TenantModel(Base):
    __tablename__ = "tenants"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    subscription_tier = Column(String(50), nullable=False, default="basic")
    is_active = Column(Boolean, default=True)
    owner_id = Column(GUID(), nullable=True)  
    settings = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship(
        "UserModel", 
        foreign_keys="UserModel.tenant_id",
        back_populates="tenant"
    )
    
    teams = relationship("TeamModel", back_populates="tenant")
    invitations = relationship("InvitationModel", back_populates="tenant")
    
    owner = relationship(
        "UserModel",
        primaryjoin="foreign(TenantModel.owner_id) == UserModel.id", 
        back_populates="owned_tenants",
        post_update=True
    )