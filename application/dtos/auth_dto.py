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


class LoginResponse(BaseModel):
    """Login response DTO."""
    
    access_token: str
    refresh_token: str
    token_type: str
    user_id: UUID
    tenant_id: Optional[UUID]
    role: str
    email: str
    full_name: str