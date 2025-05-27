from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from infrastructure.db.base import get_db
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from api.dtos.user_dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from domain.entities.user import User

router = APIRouter(prefix="/users", tags=["users"])

def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryImpl:
    return UserRepositoryImpl(db)

@router.post("/", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateDTO,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
):
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
    user = User(
        email=str(user_data.email),
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role
    )
    
    # Save to database
    created_user = user_repo.create(user)
    
    # Convert to response DTO (full_name will be computed automatically)
    return UserResponseDTO.model_validate(created_user.__dict__)

@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(
    user_id: int,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
):
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_dict = user.__dict__.copy()
    user_dict["full_name"] = user.full_name()
    response = UserResponseDTO.model_validate(user_dict)
    return response

@router.get("/", response_model=List[UserResponseDTO])
def get_users(
    skip: int = 0,
    limit: int = 100,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
):
    users = user_repo.get_all(skip=skip, limit=limit)
    response_list: List[UserResponseDTO] = []
    for user in users:
        user_dict = user.__dict__.copy()
        user_dict["full_name"] = user.full_name()
        dto = UserResponseDTO.model_validate(user_dict)
        response_list.append(dto)
    return response_list

@router.put("/{user_id}", response_model=UserResponseDTO)
def update_user(
    user_id: int,
    user_data: UserUpdateDTO,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
):
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    updated_user = user_repo.update(user)
    
    user_dict = updated_user.__dict__.copy()
    user_dict["full_name"] = updated_user.full_name()
    response = UserResponseDTO.model_validate(user_dict)
    return response

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
):
    if not user_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )