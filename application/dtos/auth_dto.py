from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID


class LoginRequest(BaseModel):
    """Login request DTO."""
    
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def password_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v


class OAuthLoginRequest(BaseModel):
    """OAuth login request DTO."""
    
    provider: str
    code: str
    redirect_uri: str
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed_providers = ['google', 'github', 'microsoft']
        if v not in allowed_providers:
            raise ValueError(f'Provider must be one of: {allowed_providers}')
        return v


class OAuthAuthorizationResponse(BaseModel):
    """OAuth authorization URL response."""
    
    authorization_url: str
    state: Optional[str] = None

class LoginResponse(BaseModel):
    """Response model for user data (without tokens)."""
    access_token: str
    refresh_token: str
    token_type: str
    user_id: UUID
    tenant_id: Optional[UUID] = None
    role: str
    email: str
    full_name: str
    bio: Optional[str] = None
    status: str = "active"
    message: Optional[str] = None
