from typing import Dict, Any
from domain.organization.entities.user import User
from domain.organization.services.auth_service import AuthService
from domain.shared.services.token_blacklist_service import TokenBlacklistService
import logging

logger = logging.getLogger(__name__)


class TokenRevocationUseCases:
    """Use cases for token revocation operations."""
    
    def __init__(
        self,
        auth_service: AuthService,
        token_blacklist_service: TokenBlacklistService
    ):
        self._auth_service = auth_service
        self._token_blacklist_service = token_blacklist_service
    
    async def logout_current_device(
        self,
        user: User,
        access_token: str,
        refresh_token: str
    ) -> bool:
        """Logout from current device only."""
        try:
            success = await self._auth_service.logout_from_current_device(
                access_token,
                refresh_token
            )
            
            if success:
                user_id = user.id.value if user.id else "unknown"
                logger.info(f"User {user_id} logged out from current device")
            
            return success
            
        except Exception as e:
            user_id = user.id.value if user.id else "unknown"
            logger.error(f"Failed to logout current device for user {user_id}: {e}")
            return False
    
    async def logout_all_devices(self, user: User) -> bool:
        """Logout from all devices."""
        try:
            if not user.id:
                raise ValueError("User ID is required")
            
            success = await self._auth_service.logout_from_all_devices(str(user.id.value))
            
            if success:
                logger.info(f"User {user.id.value} logged out from all devices")
            
            return success
            
        except Exception as e:
            user_id = user.id.value if user.id else "unknown"
            logger.error(f"Failed to logout all devices for user {user_id}: {e}")
            return False
    
    async def revoke_specific_token(self, token: str, user: User) -> bool:
        """Revoke a specific token."""
        try:
            success = await self._auth_service.revoke_token(token)
            
            if success:
                user_id = user.id.value if user.id else "unknown"
                logger.info(f"Token revoked for user {user_id}")
            
            return success
        except Exception as e:
            user_id = user.id.value if user.id else "unknown"
            logger.error(f"Failed to revoke token for user {user_id}: {e}")
            return False
    
    async def get_user_active_sessions(
        self, 
        user: User, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get active sessions for a user with pagination."""
        try:
            if not user.id:
                raise ValueError("User ID is required")
            
            user_id = str(user.id.value)
            result = await self._auth_service.get_user_active_sessions(user_id, page, page_size)
            logger.info(f"Retrieved {len(result.get('sessions', []))} active sessions for user {user_id} (page {page})")
            return result
            
        except Exception as e:
            user_id = user.id.value if user.id else "unknown"
            logger.error(f"Failed to get active sessions for user {user_id}: {e}")
            return {
                "sessions": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }

    async def get_user_revoked_sessions(
        self, 
        user: User, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get revoked sessions for a user with pagination."""
        try:
            if not user.id:
                raise ValueError("User ID is required")
            
            user_id = str(user.id.value)
            result = await self._auth_service.get_user_revoked_sessions(user_id, page, page_size)
            logger.info(f"Retrieved {len(result.get('sessions', []))} revoked sessions for user {user_id} (page {page})")
            return result
            
        except Exception as e:
            user_id = user.id.value if user.id else "unknown"
            logger.error(f"Failed to get revoked sessions for user {user_id}: {e}")
            return {
                "sessions": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens from blacklist."""
        try:
            count = await self._token_blacklist_service.cleanup_expired_tokens()
            logger.info(f"Cleaned up {count} expired tokens")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens: {e}")
            return 0
    
    async def revoke_session_by_id(self, session_id: str, user: User) -> bool:
        """Revoke a specific session by ID."""
        try:
            if not user.id:
                raise ValueError("User ID is required")
            
            success = await self._auth_service.revoke_session_by_id(
                session_id,
                str(user.id.value)
            )
            
            if success:
                logger.info(f"Session {session_id} revoked for user {user.id.value}")
            
            return success
            
        except Exception as e:
            user_id = user.id.value if user.id else "unknown"
            logger.error(f"Failed to revoke session {session_id} for user {user_id}: {e}")
            return False