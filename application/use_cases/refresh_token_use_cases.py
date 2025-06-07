from typing import Dict, Any, Optional

from domain.organization.repositories.refresh_token_repository import RefreshTokenRepository
from application.commands.refresh_token_command import (
    SaveRefreshTokenCommand,
    RevokeRefreshTokenByJtiCommand,
    RevokeRefreshTokenByIdCommand,
    RevokeAllUserRefreshTokensCommand,
    GetUserActiveSessionsCommand,
    GetUserRevokedSessionsCommand,
    GetUserActiveSessionsGroupedCommand,
    GetUserRevokedSessionsGroupedCommand,
    CleanupExpiredTokensCommand
)


class RefreshTokenUseCases:
    """Use cases for refresh token operations."""
    
    def __init__(self, refresh_token_repository: RefreshTokenRepository):
        self._refresh_token_repository = refresh_token_repository
    
    async def save_refresh_token(self, command: SaveRefreshTokenCommand) -> str:
        """Save refresh token."""
        return await self._refresh_token_repository.save_refresh_token(
            user_id=command.user_id,
            token=command.token,
            jti=command.jti,
            expires_at=command.expires_at,
            device_info=command.device_info,
            ip_address=command.ip_address,
            user_agent=command.user_agent
        )
    
    async def get_refresh_token_by_jti(self, jti: str) -> Optional[Any]:
        """Get refresh token by JWT ID."""
        return await self._refresh_token_repository.get_refresh_token_by_jti(jti)
    
    async def revoke_refresh_token_by_jti(self, command: RevokeRefreshTokenByJtiCommand) -> bool:
        """Revoke refresh token by JWT ID."""
        return await self._refresh_token_repository.revoke_refresh_token_by_jti(command.jti)
    
    async def revoke_refresh_token_by_id(self, command: RevokeRefreshTokenByIdCommand) -> bool:
        """Revoke refresh token by database ID."""
        return await self._refresh_token_repository.revoke_refresh_token_by_id(command.token_id)
    
    async def revoke_all_user_refresh_tokens(self, command: RevokeAllUserRefreshTokensCommand) -> int:
        """Revoke all refresh tokens for a user."""
        return await self._refresh_token_repository.revoke_all_user_refresh_tokens(command.user_id)
    
    async def get_user_active_sessions(self, command: GetUserActiveSessionsCommand) -> Dict[str, Any]:
        """Get user's active sessions."""
        return await self._refresh_token_repository.get_user_active_sessions(
            user_id=command.user_id,
            page=command.page,
            page_size=command.page_size
        )
    
    async def get_user_revoked_sessions(self, command: GetUserRevokedSessionsCommand) -> Dict[str, Any]:
        """Get user's revoked sessions."""
        return await self._refresh_token_repository.get_user_revoked_sessions(
            user_id=command.user_id,
            page=command.page,
            page_size=command.page_size
        )
    
    async def get_user_active_sessions_grouped(self, command: GetUserActiveSessionsGroupedCommand) -> Dict[str, Any]:
        """Get user's active sessions grouped by device and IP."""
        return await self._refresh_token_repository.get_user_active_sessions_grouped(
            user_id=command.user_id,
            page=command.page,
            page_size=command.page_size
        )
    
    async def get_user_revoked_sessions_grouped(self, command: GetUserRevokedSessionsGroupedCommand) -> Dict[str, Any]:
        """Get user's revoked sessions grouped by device and IP."""
        return await self._refresh_token_repository.get_user_revoked_sessions_grouped(
            user_id=command.user_id,
            page=command.page,
            page_size=command.page_size
        )
    
    async def cleanup_expired_tokens(self, command: CleanupExpiredTokensCommand) -> int:
        """Cleanup expired tokens."""
        return await self._refresh_token_repository.cleanup_expired_tokens()
