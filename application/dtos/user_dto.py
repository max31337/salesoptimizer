from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class UserResponse(BaseModel):
    """User response DTO."""
    user_id: str
    email: str
    role: str
    full_name: str
    tenant_id: Optional[str] = None
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
    full_name: str
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    role: str
    status: str
    is_email_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    """Update profile request DTO."""
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