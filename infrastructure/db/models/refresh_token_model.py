import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from infrastructure.db.database import Base
from infrastructure.db.models.user_model import UserModel, GUID


class RefreshTokenModel(Base):
    """Database model for tracking refresh tokens."""
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)  # Hashed token
    jti: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)  # Token ID from JWT
    device_info: Mapped[str] = mapped_column(Text, nullable=True)  # Parsed device information string
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv4/IPv6
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)  # Raw user agent string
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship to user
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[user_id],
        back_populates="refresh_tokens"
    )