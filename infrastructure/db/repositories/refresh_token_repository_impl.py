import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from infrastructure.db.models.refresh_token_model import RefreshTokenModel


class RefreshTokenRepositoryImpl:
    """Database implementation of refresh token repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save_refresh_token(
        self,
        user_id: uuid.UUID,
        token: str,
        jti: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Save refresh token and return token ID."""
        # Hash the token for security (don't store raw tokens)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        model = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            jti=jti,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self._session.add(model)
        await self._session.flush()
        
        return str(model.id)
    
    async def get_refresh_token_by_jti(self, jti: str) -> Optional[RefreshTokenModel]:
        """Get refresh token by JWT ID."""
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.jti == jti)
            .where(RefreshTokenModel.is_revoked == False)
        )
        return result.scalar_one_or_none()
    
    async def revoke_refresh_token_by_jti(self, jti: str) -> bool:
        """Revoke specific refresh token by JWT ID."""
        result = await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.jti == jti)
            .values(
                is_revoked=True,
                revoked_at=datetime.now(timezone.utc)
            )
        )
        return result.rowcount > 0
    
    async def revoke_refresh_token_by_id(self, token_id: str) -> bool:
        """Revoke specific refresh token by database ID."""
        try:
            result = await self._session.execute(
                update(RefreshTokenModel)
                .where(RefreshTokenModel.id == uuid.UUID(token_id))
                .values(
                    is_revoked=True,
                    revoked_at=datetime.now(timezone.utc)
                )
            )
            return result.rowcount > 0
        except Exception:
            return False

    async def revoke_all_user_refresh_tokens(self, user_id: uuid.UUID) -> int:
        """Revoke all refresh tokens for a user."""
        result = await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)
            .values(
                is_revoked=True,
                revoked_at=datetime.now(timezone.utc)
            )
        )
        return result.rowcount
    
    async def get_user_active_sessions(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get all active refresh tokens/sessions for a user."""
        result = await self._session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)
            .where(RefreshTokenModel.expires_at > datetime.now(timezone.utc))
            .order_by(RefreshTokenModel.created_at.desc())
        )
        
        sessions: List[Dict[str, Any]] = []
        for model in result.scalars().all():
            sessions.append({
                "id": str(model.id),
                "device_info": model.device_info,
                "ip_address": model.ip_address,
                "user_agent": model.user_agent,
                "created_at": model.created_at,
                "expires_at": model.expires_at
            })
        
        return sessions
    
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired refresh tokens."""
        result = await self._session.execute(
            delete(RefreshTokenModel)
            .where(RefreshTokenModel.expires_at < datetime.now(timezone.utc))
        )
        return result.rowcount