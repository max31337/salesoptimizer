from typing import Dict, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from application.dependencies.service_dependencies import get_application_service
from application.services.application_service import ApplicationService
from domain.services.auth_service import AuthenticationError
from application.dtos.auth_dto import (
    LoginResponse, 
    RegisterRequest, 
    RegisterResponse,
    RefreshTokenResponse,
    UserInfoResponse,
    LogoutResponse
)
from api.dependencies.auth import get_current_user
from domain.entities.user import User

router: APIRouter = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    form_data: OAuth2PasswordRequestForm = Depends()
) -> LoginResponse:
    """Authenticate user and return access token."""
    try:
        user, access_token, refresh_token = app_service.auth_use_cases.authenticate_user(
            form_data.username, 
            form_data.password
        )
        
        if user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing"
            )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            email=user.email,
            full_name=user.full_name
        )
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/register", response_model=RegisterResponse)
async def complete_registration(
    register_data: RegisterRequest,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> RegisterResponse:
    """Complete user registration with invitation token."""
    try:
        result: tuple[User, str, str] = app_service.auth_use_cases.complete_registration(
            register_data
        )
        user: User
        access_token: str
        refresh_token: str
        user, access_token, refresh_token = result
        
        if user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing"
            )
        
        return RegisterResponse(
            message="Registration completed successfully",
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            tenant_id=user.tenant_id
        )
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserInfoResponse:
    """Get current user information."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing"
        )
    return UserInfoResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.value,
        full_name=current_user.full_name,
        tenant_id=current_user.tenant_id,
        status=current_user.status.value,
        is_email_verified=current_user.is_email_verified
    )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    refresh_data: Dict[str, str] = Body(
        ...,
        examples=[
            {
                "summary": "Refresh Token Example",
                "description": "Example of refresh token request",
                "value": {"refresh_token": "5c74659c-429a-4633-8c9d-a342a059994a"}
            }
        ]
    )
) -> RefreshTokenResponse:
    """Refresh access token using refresh token."""
    try:
        if "refresh_token" not in refresh_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing refresh_token in request body"
            )
        
        access_token, new_refresh_token = app_service.auth_use_cases.refresh_tokens(
            refresh_data["refresh_token"]
        )
        
        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/logout", response_model=LogoutResponse)
async def logout() -> LogoutResponse:
    """Logout user (client-side token removal)."""
    return LogoutResponse(message="Successfully logged out")
