from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, computed_field, ConfigDict
from domain.organization.entities.user import UserRole, UserStatus

class UserCreateDTO(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.SALES_REP

class UserUpdateDTO(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str 
    email: str
    username: str
    first_name: str
    last_name: str
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

class UserListResponseDTO(BaseModel):
    users: list[UserResponseDTO]
    total: int
    skip: int
    limit: int

class UserCreateResponseDTO(BaseModel):
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    message: str = "User created successfully"