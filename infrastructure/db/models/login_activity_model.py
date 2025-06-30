
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as GUID
from typing import Optional
import uuid
from datetime import datetime, timezone
from infrastructure.db.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from infrastructure.db.models.user_model import UserModel

class LoginActivityModel(Base):
    __tablename__ = "login_activity"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    logout_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv4/IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="login_activities")
