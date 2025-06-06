from abc import ABC, abstractmethod
from typing import Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TokenBlacklistService(ABC):
    """Abstract service for managing token blacklist."""
    
    @abstractmethod
    async def revoke_token(self, token: str, revoked_at: datetime) -> bool:
        """Add token to blacklist."""
        pass
    
    @abstractmethod
    async def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked."""
        pass
    
    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: str, revoked_at: datetime) -> int:
        """Revoke all tokens for a specific user."""
        pass
    
    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from blacklist."""
        pass


class InMemoryTokenBlacklistService(TokenBlacklistService):
    """In-memory implementation for development/testing."""
    
    def __init__(self):
        self._blacklisted_tokens: Set[str] = set()
        self._user_revocation_times: dict[str, datetime] = {}
    
    async def revoke_token(self, token: str, revoked_at: datetime) -> bool:
        """Add token to blacklist."""
        self._blacklisted_tokens.add(token)
        logger.info(f"Token revoked at {revoked_at}")
        return True
    
    async def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked."""
        return token in self._blacklisted_tokens
    
    async def revoke_all_user_tokens(self, user_id: str, revoked_at: datetime) -> int:
        """Revoke all tokens for a specific user by timestamp."""
        self._user_revocation_times[user_id] = revoked_at
        logger.info(f"All tokens for user {user_id} revoked at {revoked_at}")
        return 1  # Simulated count
    
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from blacklist."""
        # In real implementation, would check token expiry
        count = len(self._blacklisted_tokens)
        self._blacklisted_tokens.clear()
        return count

    async def is_user_token_revoked(self, user_id: str, token_issued_at: datetime) -> bool:
        """Check if user's token was issued before global revocation."""
        user_revocation_time = self._user_revocation_times.get(user_id)
        if user_revocation_time and token_issued_at < user_revocation_time:
            return True
        return False