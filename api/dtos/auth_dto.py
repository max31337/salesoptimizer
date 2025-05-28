from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def password_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: UUID
    tenant_id: Optional[UUID]
    role: str
    email: str
    full_name: str

class RegisterRequest(BaseModel):
    invitation_token: str
    password: str
    first_name: str
    last_name: str
    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def names_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @field_validator('invitation_token')
    @classmethod
    def invitation_token_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Invitation token cannot be empty')
        return v
        return v

class RegisterResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    user_id: UUID
    tenant_id: Optional[UUID]
    @field_validator('refresh_token')
    @classmethod
    def token_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Refresh token cannot be empty')
        return v

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserInfoResponse(BaseModel):
    id: UUID
    email: str
    username: Optional[str]
    first_name: str
    last_name: str
    role: str
    full_name: str
    tenant_id: Optional[UUID]
    status: str
    is_email_verified: bool
    
    class Config:
        from_attributes = True

class LogoutResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None