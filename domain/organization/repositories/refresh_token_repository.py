from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class RefreshTokenRepository(ABC):
    """Repository interface for refresh token operations."""
    
    @abstractmethod
    async def save_refresh_token(
        self,
        user_id: UUID,
        token: str,
        jti: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Save refresh token and return token ID."""
        pass
    
    @abstractmethod
    async def get_refresh_token_by_jti(self, jti: str) -> Optional[Any]:
        """Get refresh token by JWT ID."""
        pass
    
    @abstractmethod
    async def revoke_refresh_token_by_jti(self, jti: str) -> bool:
        """Revoke specific refresh token by JWT ID."""
        pass
    
    @abstractmethod
    async def revoke_refresh_token_by_id(self, token_id: str) -> bool:
        """Revoke specific refresh token by database ID."""
        pass
    
    @abstractmethod
    async def revoke_all_user_refresh_tokens(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user."""
        pass
    
    @abstractmethod
    async def get_user_active_sessions(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get all active refresh tokens/sessions for a user with pagination."""
        pass
    
    @abstractmethod
    async def get_user_revoked_sessions(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get all revoked refresh tokens/sessions for a user with pagination."""
        pass
    
    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired refresh tokens."""
        pass
    
    @abstractmethod
    async def get_user_active_sessions_grouped_by_device(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get active sessions grouped by device."""
        pass
    
    @abstractmethod
    async def get_user_active_sessions_grouped_by_ip(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get active sessions grouped by IP address."""
        pass
    
    @abstractmethod
    async def get_user_revoked_sessions_grouped_by_device(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get revoked sessions grouped by device."""
        pass
    
    @abstractmethod
    async def get_user_revoked_sessions_grouped_by_ip(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get revoked sessions grouped by IP address."""
        pass

    async def get_user_revoked_sessions(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get user's revoked sessions."""
        raise NotImplementedError
    
    async def get_user_active_sessions_grouped(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get user's active sessions grouped by device and IP."""
        raise NotImplementedError
    
    async def get_user_revoked_sessions_grouped(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get user's revoked sessions grouped by device and IP."""
        raise NotImplementedError