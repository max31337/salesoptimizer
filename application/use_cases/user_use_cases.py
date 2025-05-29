from typing import Optional
from uuid import UUID
from typing import List
from domain.entities.user import User, UserStatus
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from application.dtos.user_dto import UserCreateDTO, UserResponseDTO, UserUpdateDTO


class UserUseCases:
    def __init__(self, user_repository: UserRepositoryImpl):
        self.user_repository = user_repository
    
    def create_user(self, user_data: UserCreateDTO) -> UserResponseDTO:
        """Create a new user."""
        # Check if email or username already exists
        if self.user_repository.exists_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        if self.user_repository.exists_by_username(user_data.username):
            raise ValueError("Username already taken")
        
        # Create user entity
        user = User(
            email=str(user_data.email),
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_data.role,
            status=UserStatus.ACTIVE
        )
        
        # Save to database
        created_user = self.user_repository.create(user)
        
        # Convert to response DTO
        return UserResponseDTO(
            id=str(created_user.id),
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
    
    def get_user_by_id(self, user_id: str) -> Optional[UserResponseDTO]:
        """Get user by ID."""
        user = self.user_repository.get_by_id(UUID(user_id))
        if not user:
            return None
        
        return UserResponseDTO(
            id=str(user.id),
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

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponseDTO]:
        """
        Retrieve all users with pagination.
        """
        users = self.user_repository.get_all(skip=skip, limit=limit)
        return [
            UserResponseDTO(
                id=str(user.id),
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
            ) for user in users
        ]
    

    def update_user(self, user_id: str, user_data: UserUpdateDTO) -> UserResponseDTO:
        """
        Update a user by ID.
        """
        # Retrieve the user using the repository
        user = self.user_repository.get_by_id(UUID(user_id))
        if not user:
            raise ValueError("User not found")
        # Update user fields
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        # Save the updated user
        updated_user = self.user_repository.update(user)
        return UserResponseDTO(
            id=str(updated_user.id),
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
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID. Returns True if deleted, False if not found."""
        user = self.user_repository.get_by_id(UUID(user_id))
        if not user:
            return False
        if user.id is None:
            raise ValueError("User ID is None, cannot delete user")
        self.user_repository.delete(user.id)
        return True
