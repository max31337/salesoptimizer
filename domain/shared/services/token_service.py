from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


class TokenService(ABC):
    """Domain service interface for token operations."""
    
    @abstractmethod
    async def save_refresh_token_to_storage(
        self,
        user_id: str,
        token: str,
        jti: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Save refresh token to storage."""
        pass
    
    @abstractmethod
    async def revoke_refresh_token_by_jti(self, jti: str) -> bool:
        """Revoke refresh token by JWT ID."""
        pass
    
    @abstractmethod
    async def revoke_access_token(self, jti: str) -> bool:
        """Revoke access token."""
        pass
