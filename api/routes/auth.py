from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict
from infrastructure.db.base import get_db
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from domain.services.auth_service import AuthService, AuthenticationError
from api.dtos.auth_dto import (
    LoginResponse, RegisterRequest, RegisterResponse, 
    RefreshTokenResponse, UserInfoResponse, LogoutResponse
)
from fastapi import Body
from api.dependencies.auth import get_current_user
from domain.entities.user import User

router: APIRouter = APIRouter(prefix="/auth", tags=["authentication"])
security: HTTPBearer = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get auth service."""
    user_repo: UserRepositoryImpl = UserRepositoryImpl(db)
    password_service: PasswordService = PasswordService()
    jwt_service: JWTService = JWTService()
    return AuthService(user_repo, password_service, jwt_service)

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """Authenticate user and return access token."""
    try:
        user: User = auth_service.authenticate_user(form_data.username, form_data.password)
        access_token: str
        refresh_token: str
        access_token, refresh_token = auth_service.create_user_tokens(user)
        
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
    auth_service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    """Complete user registration with invitation token."""
    try:
        user: User = auth_service.complete_registration(
            invitation_token=register_data.invitation_token,
            password=register_data.password,
            first_name=register_data.first_name,
            last_name=register_data.last_name
        )
        
        access_token: str
        refresh_token: str
        access_token, refresh_token = auth_service.create_user_tokens(user)
        
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
    current_user: User = Depends(get_current_user)
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
    refresh_data: Dict[str, str] = Body(
        ...,
        example={"refresh_token": "your_refresh_token"}
    ),
    auth_service: AuthService = Depends(get_auth_service)
) -> RefreshTokenResponse:
    """Refresh access token using refresh token."""
    try:
        access_token: str
        new_refresh_token: str
        access_token, new_refresh_token = auth_service.refresh_user_tokens(refresh_data["refresh_token"])
        
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