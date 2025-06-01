from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from application.dependencies.service_dependencies import (
    get_application_service,
    ApplicationService
)
from application.dtos.auth_dto import (
    LoginResponse, 
    OAuthAuthorizationResponse
)
from application.commands.auth_command import LoginCommand
from application.commands.oauth_command import OAuthLoginCommand, OAuthAuthorizationCommand
from domain.organization.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    form_data: OAuth2PasswordRequestForm = Depends()
) -> LoginResponse:
    """Authenticate user and return access token."""
    
    try:
        # Create login command
        command = LoginCommand(
            email_or_username=form_data.username,
            password=form_data.password
        )
        
        # Execute login use case
        user, access_token, refresh_token = await app_service.auth_use_cases.login(command)
        
        if not user.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing"
            )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id.value,
            tenant_id=user.tenant_id,
            role=user.role.value,
            email=str(user.email),
            full_name=user.full_name
        )
    
    except (InvalidCredentialsError, UserNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active"
        )
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/oauth/{provider}/authorize")
async def oauth_authorize(
    provider: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    redirect_uri: str = Query(..., description="Redirect URI after authentication")
) -> OAuthAuthorizationResponse:
    """Get OAuth authorization URL."""
    try:
        # Check if provider is configured
        if not app_service.config.is_provider_configured(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider}' is not configured"
            )
        
        command = OAuthAuthorizationCommand(
            provider=provider,
            redirect_uri=redirect_uri
        )
        
        authorization_url = app_service.auth_use_cases.get_oauth_authorization_url(command)
        
        return OAuthAuthorizationResponse(authorization_url=authorization_url)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.post("/oauth/{provider}/callback", response_model=LoginResponse)
async def oauth_callback(
    provider: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    code: str = Query(..., description="Authorization code from OAuth provider"),
    redirect_uri: str = Query(..., description="Redirect URI used in authorization")
) -> LoginResponse:
    """Handle OAuth callback and authenticate user."""
    try:
        command = OAuthLoginCommand(
            provider=provider,
            code=code,
            redirect_uri=redirect_uri
        )
        
        user, access_token, refresh_token, is_new_user = await app_service.auth_use_cases.oauth_login(command)
        
        if not user.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing"
            )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id.value,
            tenant_id=user.tenant_id,
            role=user.role.value,
            email=str(user.email),
            full_name=user.full_name,
            is_new_user=is_new_user
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/oauth/{provider}/login")
async def oauth_login_redirect(
    provider: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> RedirectResponse:
    """Redirect to OAuth provider for authentication."""
    try:
        # Check if provider is configured
        if not app_service.config.is_provider_configured(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider}' is not configured"
            )
        
        # Use provider-specific redirect URL
        redirect_uri = f"http://localhost:8000/api/v1/auth/oauth/{provider}/callback"
        
        command = OAuthAuthorizationCommand(
            provider=provider,
            redirect_uri=redirect_uri
        )
        
        authorization_url = app_service.auth_use_cases.get_oauth_authorization_url(command)
        
        return RedirectResponse(url=authorization_url)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.get("/oauth/config")
async def oauth_config(
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> Dict[str, Any]:
    """Get OAuth configuration status."""
    return {
        "providers": {
            "google": {
                "configured": app_service.config.is_provider_configured("google"),
                "client_id": app_service.config.google_client_id[:10] + "..." if app_service.config.google_client_id else None
            },
            "github": {
                "configured": app_service.config.is_provider_configured("github"),
                "client_id": app_service.config.github_client_id[:10] + "..." if app_service.config.github_client_id else None
            },
            "microsoft": {
                "configured": app_service.config.is_provider_configured("microsoft"),
                "client_id": app_service.config.microsoft_client_id[:10] + "..." if app_service.config.microsoft_client_id else None
            }
        },
        "frontend_url": app_service.config.frontend_url
    }