import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Optional
import json
import logging

from domain.shared.services.token_blacklist_service import TokenBlacklistService

logger = logging.getLogger(__name__)


class RedisTokenBlacklistService(TokenBlacklistService):
    """Redis-based token blacklist service for production."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
    
    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection."""
        if self._redis is None:
            self._redis = await redis.from_url(str(self.redis_url), decode_responses=True) # type: ignore
        return self._redis
    
    async def revoke_token(self, token: str, revoked_at: datetime) -> bool:
        """Add token to blacklist with expiration."""
        try:
            redis_client = await self._get_redis()
            
            # Store token with expiration (JWT expiry + buffer)
            token_data = {
                "revoked_at": revoked_at.isoformat(),
                "reason": "manual_revocation"
            }
            
            # Set expiration to 24 hours (adjust based on your token expiry)
            await redis_client.setex(
                f"blacklist:token:{token}",
                timedelta(hours=24),
                json.dumps(token_data)
            )
            
            logger.info(f"Token revoked and stored in Redis at {revoked_at}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke token in Redis: {e}")
            return False
    
    async def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked."""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.get(f"blacklist:token:{token}")
            return result is not None
            
        except Exception as e:
            logger.error(f"Failed to check token revocation in Redis: {e}")
            return False
    
    async def revoke_all_user_tokens(self, user_id: str, revoked_at: datetime) -> int:
        """Revoke all tokens for a specific user."""
        try:
            redis_client = await self._get_redis()
            
            # Store user revocation timestamp
            await redis_client.setex(
                f"blacklist:user:{user_id}",
                timedelta(days=7),  # Keep for 7 days
                revoked_at.isoformat()
            )
            
            logger.info(f"All tokens for user {user_id} revoked at {revoked_at}")
            return 1
            
        except Exception as e:
            logger.error(f"Failed to revoke user tokens in Redis: {e}")
            return 0
    
    async def is_user_token_revoked(self, user_id: str, token_issued_at: datetime) -> bool:
        """Check if user's token was issued before global revocation."""
        try:
            redis_client = await self._get_redis()
            revocation_time_str = await redis_client.get(f"blacklist:user:{user_id}")
            
            if revocation_time_str:
                revocation_time = datetime.fromisoformat(revocation_time_str)
                return token_issued_at < revocation_time
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check user token revocation in Redis: {e}")
            return False
    
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from blacklist."""
        try:
            redis_client = await self._get_redis()
            
            # Redis automatically handles expiration, but we can scan for cleanup
            cursor = 0
            count = 0
            
            while True:
                scan_result = await redis_client.scan( # type: ignore
                    cursor=cursor,
                    match="blacklist:token:*",
                    count=100
                )
                cursor, keys = scan_result
                
                if keys:
                    # Check which keys still exist (non-expired)
                    existing_keys = await redis_client.exists(*keys)
                    count += len(keys) - existing_keys
                
                if cursor == 0:
                    break
            
            logger.info(f"Cleaned up {count} expired tokens")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens in Redis: {e}")
            return 0
    
    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()