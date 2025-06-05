from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    """User response DTO."""
    user_id: str
    email: str
    role: str
    full_name: str
    tenant_id: Optional[str] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True