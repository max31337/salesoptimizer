from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from application.services.application_service import (
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

from infrastructure.dependencies.service_container import get_application_service


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    form_data: OAuth2PasswordRequestForm = Depends()
) -> LoginResponse:
    """Authenticate user and return access token."""
    
    try:
        command = LoginCommand(
            email_or_username=form_data.username,
            password=form_data.password
        )
        
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


#===============================================================================
#                              🔐 OAuth2 Routes                                |
#===============================================================================

@router.get("/oauth/{provider}/authorize")
async def oauth_authorize(
    provider: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    redirect_uri: str = Query(None, description="Custom redirect URI (optional)")
) -> OAuthAuthorizationResponse:
    """Get OAuth authorization URL."""
    try:
        if not app_service.config.is_provider_configured(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider}' is not configured"
            )
        
        # Use provided redirect_uri or default from config
        final_redirect_uri = redirect_uri or app_service.config.get_redirect_url(provider)
        
        command = OAuthAuthorizationCommand(
            provider=provider,
            redirect_uri=final_redirect_uri
        )
        
        authorization_url = app_service.auth_use_cases.get_oauth_authorization_url(command)
        
        return OAuthAuthorizationResponse(authorization_url=authorization_url)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/oauth/{provider}/login")
async def oauth_login_redirect(
    provider: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> RedirectResponse:
    """Step 2: Redirect to OAuth provider for authentication."""
    try:
        if not app_service.config.is_provider_configured(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider}' is not configured"
            )
        
        # Step 3: Use BACKEND callback URL (port 8000)
        redirect_uri = app_service.config.get_redirect_url(provider)
        
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


@router.get("/oauth/{provider}/callback")
async def oauth_callback_get(
    provider: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(None, description="State parameter"),
    error: str = Query(None, description="Error from OAuth provider")
):
    """Step 4-6: Handle OAuth callback and redirect to frontend."""
    if error:
        error_url = f"{app_service.config.frontend_url}/auth/error?error={error}"
        return RedirectResponse(url=error_url)
    
    try:
        # Step 5: Use the same BACKEND redirect URI that was sent to the provider
        redirect_uri = app_service.config.get_redirect_url(provider)
        
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
        
        # Step 6: Redirect to FRONTEND with tokens
        success_url = f"{app_service.config.frontend_url}/auth/success?token={access_token}&refresh_token={refresh_token}&new_user={is_new_user}&provider={provider}"
        return RedirectResponse(url=success_url)
    
    except ValueError as e:
        error_url = f"{app_service.config.frontend_url}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)
    except AuthenticationError as e:
        error_url = f"{app_service.config.frontend_url}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/oauth/config")
async def oauth_config(
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> Dict[str, Any]:
    """Get OAuth configuration status."""
    return {
        "providers": {
            "google": {
                "configured": app_service.config.is_provider_configured("google"),
                "client_id": app_service.config.google_client_id[:10] + "..." if app_service.config.google_client_id else None,
                "redirect_url": app_service.config.get_redirect_url("google") if app_service.config.is_provider_configured("google") else None
            },
            "github": {
                "configured": app_service.config.is_provider_configured("github"),
                "client_id": app_service.config.github_client_id[:10] + "..." if app_service.config.github_client_id else None,
                "redirect_url": app_service.config.get_redirect_url("github") if app_service.config.is_provider_configured("github") else None
            },
            "microsoft": {
                "configured": app_service.config.is_provider_configured("microsoft"),
                "client_id": app_service.config.microsoft_client_id[:10] + "..." if app_service.config.microsoft_client_id else None,
                "redirect_url": app_service.config.get_redirect_url("microsoft") if app_service.config.is_provider_configured("microsoft") else None
            }
        },
        "frontend_url": app_service.config.frontend_url
    }


#===============================================================================
#                              🔐 Organization Routes                          |
#===============================================================================

