from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from infrastructure.db.models.base import Base
from infrastructure.db.models.user_model import GUID

class TeamModel(Base):
    __tablename__ = "teams"
    
    id = Column(GUID(), primary_key=True)
    tenant_id = Column(GUID(), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="teams")
    manager = relationship("UserModel", foreign_keys=[manager_id], back_populates="managed_teams")
    members = relationship("UserModel", foreign_keys="UserModel.team_id", back_populates="team")