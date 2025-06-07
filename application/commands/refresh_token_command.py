from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class SaveRefreshTokenCommand:
    """Command to save refresh token."""
    user_id: UUID
    token: str
    jti: str
    expires_at: datetime
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class RevokeRefreshTokenByJtiCommand:
    """Command to revoke refresh token by JWT ID."""
    jti: str


@dataclass
class RevokeRefreshTokenByIdCommand:
    """Command to revoke refresh token by database ID."""
    token_id: str


@dataclass
class RevokeAllUserRefreshTokensCommand:
    """Command to revoke all refresh tokens for a user."""
    user_id: UUID


@dataclass
class GetUserActiveSessionsCommand:
    """Command to get user's active sessions."""
    user_id: UUID
    page: int = 1
    page_size: int = 10


@dataclass
class GetUserRevokedSessionsCommand:
    """Command to get user's revoked sessions."""
    user_id: UUID
    page: int = 1
    page_size: int = 10


@dataclass
class GetUserActiveSessionsGroupedCommand:
    """Command to get user's active sessions grouped by device or IP."""
    user_id: UUID
    group_by: str  # 'device' or 'ip'
    page: int = 1
    page_size: int = 10


@dataclass
class GetUserRevokedSessionsGroupedCommand:
    """Command to get user's revoked sessions grouped by device or IP."""
    user_id: UUID
    group_by: str  # 'device' or 'ip'
    page: int = 1
    page_size: int = 10


@dataclass
class CleanupExpiredTokensCommand:
    """Command to cleanup expired tokens."""
    pass
