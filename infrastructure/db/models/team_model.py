import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from infrastructure.db.base import Base
from infrastructure.db.models.user_model import GUID

class TeamModel(Base):
    __tablename__ = "teams"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID(), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(GUID(), nullable=True)  # No FK constraint to avoid circular dependency
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships with explicit primaryjoin
    tenant = relationship("TenantModel", back_populates="teams")
    
    # Team manager (no FK constraint, so we need primaryjoin)
    manager = relationship(
        "UserModel", 
        primaryjoin="TeamModel.manager_id == UserModel.id",
        foreign_keys=[manager_id],
        back_populates="managed_teams",
        post_update=True
    )
    
    # Team members (FK exists, so this works normally)
    members = relationship(
        "UserModel", 
        foreign_keys="UserModel.team_id", 
        back_populates="team"
    )