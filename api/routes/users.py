from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from application.dependencies.service_dependencies import get_application_service
from application.services.application_service import ApplicationService
from application.dtos.user_dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO

router: APIRouter = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateDTO,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> UserResponseDTO:
    """Create a new user."""
    try:
        return app_service.user_use_cases.create_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(
    user_id: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> UserResponseDTO:
    """Get user by ID."""
    user = app_service.user_use_cases.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/", response_model=List[UserResponseDTO])
def get_users(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    skip: int = 0,
    limit: int = 100
) -> List[UserResponseDTO]:
    """Get all users with pagination."""
    return app_service.user_use_cases.get_all_users(skip=skip, limit=limit)

@router.put("/{user_id}", response_model=UserResponseDTO)
def update_user(
    user_id: str,
    user_data: UserUpdateDTO,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> UserResponseDTO:
    """Update user by ID."""
    try:
        return app_service.user_use_cases.update_user(user_id, user_data)
    except ValueError as e:
        if "User not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
):
    """Delete user by ID."""
    success = app_service.user_use_cases.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )