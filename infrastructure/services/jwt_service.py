import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID
import os

class JWTService:
    """Service for JWT token creation and verification with strict type hints."""
    
    def __init__(self) -> None:
        self.secret_key: str = os.getenv("JWT_SECRET_KEY", "")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY must be set")
        if len(self.secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        
        self.algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.invitation_token_expire_hours: int = 48  # Default 48 hours

    def create_access_token(
        self, 
        user_id: UUID, 
        tenant_id: Optional[UUID], 
        role: str, 
        email: str
    ) -> str:
        """Create access token for authenticated user."""
        expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id) if tenant_id else None,
            "role": role,
            "email": email,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create refresh token for token renewal."""
        expire: datetime = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_invitation_token(
        self, 
        email: str, 
        tenant_id: Optional[UUID], 
        role: str,
        expires_hours: Optional[int] = None
    ) -> str:
        """Create invitation token for user registration."""
        if expires_hours is None:
            expires_hours = self.invitation_token_expire_hours
            
        expire: datetime = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
        
        payload: Dict[str, Any] = {
            "email": email,
            "tenant_id": str(tenant_id) if tenant_id else None,
            "role": role,
            "type": "invitation",
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        if not token:
            return None
            
        # Remove Bearer prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        try:
            payload: Dict[str, Any] = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
        

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode a JWT token and return the payload."""
        # Replace 'your-secret-key' and 'HS256' with your actual secret and algorithm
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise
        except Exception:
            raise

    def decode_token_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification (for debugging only)."""
        if not token:
            return None
            
        # Remove Bearer prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
            
        try:
            payload: Dict[str, Any] = jwt.decode(
                token, 
                options={"verify_signature": False}
            )
            return payload
        except Exception:
            return None

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get token expiry time."""
        payload: Optional[Dict[str, Any]] = self.decode_token_without_verification(token)
        if payload and "exp" in payload:
            try:
                return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                return None
        return None

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired."""
        expiry: Optional[datetime] = self.get_token_expiry(token)
        if expiry:
            return datetime.now(timezone.utc) > expiry
        return True

    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract the user ID ('sub' claim) from the given JWT token.
        Returns the user ID as a string, or None if extraction fails.
        """
        payload: Optional[Dict[str, Any]] = self.verify_token(token)
        if payload and "sub" in payload:
            sub_claim: Any = payload["sub"]
            if isinstance(sub_claim, str):
                return sub_claim
            elif sub_claim is not None:
                return str(sub_claim)
        return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Create new access token from refresh token."""
        payload: Optional[Dict[str, Any]] = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str:
            return None
        
        try:
            user_id: UUID = UUID(user_id_str)
            # Note: In a real implementation, you'd fetch user data from database
            # For now, we'll create a basic access token
            return self.create_access_token(
                user_id=user_id,
                tenant_id=None,  # Would be fetched from database
                role="sales_rep",  # Would be fetched from database
                email=""  # Would be fetched from database
            )
        except ValueError:
            return None

    def validate_token_type(self, token: str, expected_type: str) -> bool:
        """Validate that token is of expected type."""
        payload: Optional[Dict[str, Any]] = self.verify_token(token)
        if not payload:
            return False
        return payload.get("type") == expected_type

    def get_token_claims(self, token: str) -> Optional[Dict[str, Any]]:
        """Get all claims from token if valid."""
        return self.verify_token(token)

    def extract_email_from_token(self, token: str) -> Optional[str]:
        """Extract email from token if present."""
        payload: Optional[Dict[str, Any]] = self.verify_token(token)
        if payload and "email" in payload:
            email_claim: Any = payload["email"]
            if isinstance(email_claim, str):
                return email_claim
        return None

    def extract_role_from_token(self, token: str) -> Optional[str]:
        """Extract role from token if present."""
        payload: Optional[Dict[str, Any]] = self.verify_token(token)
        if payload and "role" in payload:
            role_claim: Any = payload["role"]
            if isinstance(role_claim, str):
                return role_claim
        return None

    def extract_tenant_id_from_token(self, token: str) -> Optional[str]:
        """Extract tenant ID from token if present."""
        payload: Optional[Dict[str, Any]] = self.verify_token(token)
        if payload and "tenant_id" in payload:
            tenant_id_claim: Any = payload["tenant_id"]
            if isinstance(tenant_id_claim, str):
                return tenant_id_claim
            elif tenant_id_claim is not None:
                return str(tenant_id_claim)
        return None