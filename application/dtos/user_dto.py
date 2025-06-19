from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TeamInfoResponse(BaseModel):
    """Team information for user profile."""
    id: str
    name: str
    description: Optional[str] = None
    member_count: int
    manager_name: Optional[str] = None
    is_active: bool

class UserResponse(BaseModel):
    """User response DTO."""
    user_id: str
    email: str
    role: str
    first_name: str
    last_name: str
    tenant_id: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    profile_picture_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    """User profile response DTO."""
    user_id: str
    email: str
    username: Optional[str] = None
    first_name: str
    last_name: str
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    role: str
    status: str
    password_strength: Optional[str] = None
    is_email_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileAdminResponse(UserProfileResponse):
    """User profile response DTO for admins (includes all technical details)."""
    tenant_id: Optional[str] = None
    team_id: Optional[str] = None
    team_info: Optional[TeamInfoResponse] = None

class UserProfilePublicResponse(BaseModel):
    """User profile response DTO for regular users (no UUIDs exposed)."""
    email: str
    username: Optional[str] = None
    first_name: str
    last_name: str
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    role: str
    status: str
    password_strength: Optional[str] = None
    is_email_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    team_info: Optional[TeamInfoResponse] = None
    
    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    """Update profile request DTO."""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UpdateProfileByAdminRequest(BaseModel):
    """Update profile by admin request DTO."""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

class ProfileUpdatePendingResponse(BaseModel):
    """Profile update pending approval response DTO."""
    message: str
    requires_approval: bool = True
    pending_changes: Dict[str, Any]