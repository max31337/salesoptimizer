from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from infrastructure.db.base import get_db
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from api.dtos.user_dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from domain.entities.user import User, UserStatus

router: APIRouter = APIRouter(prefix="/users", tags=["users"])

def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryImpl:
    """Dependency to get user repository."""
    return UserRepositoryImpl(db)

@router.post("/", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateDTO,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> UserResponseDTO:
    """Create a new user."""
    # Check if email or username already exists
    if user_repo.exists_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user_repo.exists_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user entity
    user: User = User(
        email=str(user_data.email),
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        status=UserStatus.ACTIVE  # Set default status
    )
    
    # Save to database
    created_user: User = user_repo.create(user)
    
    # Convert to response DTO
    return UserResponseDTO(
        id=str(created_user.id) if created_user.id else "",
        email=created_user.email,
        username=created_user.username or "",
        first_name=created_user.first_name,
        last_name=created_user.last_name,
        phone=created_user.phone,
        role=created_user.role,
        status=created_user.status,
        is_email_verified=created_user.is_email_verified,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at,
        last_login=created_user.last_login
    )

@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(
    user_id: str,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> UserResponseDTO:
    """Get user by ID."""
    try:
        uuid_id: UUID = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user: Optional[User] = user_repo.get_by_id(uuid_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponseDTO(
        id=str(user.id) if user.id else "",
        email=user.email,
        username=user.username or "",
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
        status=user.status,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login
    )

@router.get("/", response_model=List[UserResponseDTO])
def get_users(
    skip: int = 0,
    limit: int = 100,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> List[UserResponseDTO]:
    """Get all users with pagination."""
    users: List[User] = user_repo.get_all(skip=skip, limit=limit)
    
    response_list: List[UserResponseDTO] = []
    for user in users:
        dto: UserResponseDTO = UserResponseDTO(
            id=str(user.id) if user.id else "",
            email=user.email,
            username=user.username or "",
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            status=user.status,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        response_list.append(dto)
    
    return response_list

@router.put("/{user_id}", response_model=UserResponseDTO)
def update_user(
    user_id: str,
    user_data: UserUpdateDTO,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> UserResponseDTO:
    """Update user by ID."""
    try:
        uuid_id: UUID = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user: Optional[User] = user_repo.get_by_id(uuid_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    from typing import Any
    update_data: dict[str, Any] = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    updated_user: User = user_repo.update(user)
    
    return UserResponseDTO(
        id=str(updated_user.id) if updated_user.id else "",
        email=updated_user.email,
        username=updated_user.username or "",
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        phone=updated_user.phone,
        role=updated_user.role,
        status=updated_user.status,
        is_email_verified=updated_user.is_email_verified,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        last_login=updated_user.last_login
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> None:
    """Delete user by ID."""
    try:
        uuid_id: UUID = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    success: bool = user_repo.delete(uuid_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )