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

class ChangePasswordRequest(BaseModel):
    """Change password request DTO."""
    
    current_password: str
    new_password: str
    
    @field_validator('current_password')
    @classmethod
    def current_password_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Current password cannot be empty')
        return v
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('New password cannot be empty')
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v


class LoginResponse(BaseModel):
    """Response model for user data (without tokens)."""
    access_token: str
    refresh_token: str
    token_type: str
    user_id: UUID
    tenant_id: Optional[UUID] = None
    role: str
    email: str
    first_name: str
    last_name: str
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    status: str = "active"
    message: Optional[str] = None

    class Config:
        from_attributes = True

