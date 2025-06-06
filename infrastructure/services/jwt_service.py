import jwt
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Union
import uuid
import logging
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class JWTService:
    def __init__(
        self,
        secret_key: str = settings.JWT_SECRET_KEY,
        algorithm: str = settings.JWT_ALGORITHM if hasattr(settings, 'JWT_ALGORITHM') else "HS256",
        access_token_expire_minutes: int = settings.JWT_EXPIRE_MINUTES if hasattr(settings, 'JWT_EXPIRE_MINUTES') else 30,
        refresh_token_expire_days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS if hasattr(settings, 'REFRESH_TOKEN_EXPIRE_DAYS') else 7,
        token_blacklist_service: Optional[Any] = None,
        refresh_token_repository: Optional[Any] = None
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.token_blacklist_service = token_blacklist_service
        self.refresh_token_repository = refresh_token_repository
    
    def create_access_token(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        role: str = "user",
        email: str = ""
    ) -> str:
        """Create access token."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload: Dict[str, Union[str, int, None]] = {
            "sub": user_id,
            "email": email,
            "role": role,
            "tenant_id": tenant_id,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4())  # Unique token ID for revocation
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token (simple version for now)."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload: Dict[str, Union[str, int]] = {
            "sub": user_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4())  # Unique token ID for revocation
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
      # For now, create a simple async version that calls the sync version
    async def create_refresh_token_with_storage(
        self, 
        user_id: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Create refresh token with database storage."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        jti = str(uuid.uuid4())
        
        payload: Dict[str, Union[str, int]] = {
            "sub": user_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": jti
        }
        
        refresh_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token in database if repository is available
        if self.refresh_token_repository:
            try:
                await self.refresh_token_repository.save_refresh_token(
                    user_id=uuid.UUID(user_id),
                    token=refresh_token,
                    jti=jti,
                    expires_at=expire,
                    device_info=device_info,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                logger.info(f"Refresh token stored in database for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to store refresh token in database: {e}")
                # Continue without database storage for now
                
        return refresh_token
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token (async version) with comprehensive blacklist checking."""
        try:
            # First decode the token to get payload
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is blacklisted (if service is available)
            if self.token_blacklist_service:
                # Check if specific token is revoked
                if await self.token_blacklist_service.is_token_revoked(token):
                    logger.warning("Token is specifically revoked")
                    return None
                
                # Check if user's tokens were revoked globally
                user_id = payload.get("sub")
                token_issued_at_timestamp = payload.get("iat")
                if user_id and token_issued_at_timestamp:
                    from datetime import datetime, timezone
                    token_issued_at = datetime.fromtimestamp(token_issued_at_timestamp, tz=timezone.utc)
                    if await self.token_blacklist_service.is_user_token_revoked(user_id, token_issued_at):
                        logger.warning(f"User {user_id} tokens were globally revoked")
                        return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def verify_token_sync(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token (sync version for backward compatibility)."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """Extract user ID from token without verification."""
        try:
            # Decode without verification to get payload
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("sub")
        except Exception:
            return None
    
    def validate_token_type(self, token: str, expected_type: str) -> bool:
        """Validate token type (access/refresh)."""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("type") == expected_type
        except Exception:
            return False