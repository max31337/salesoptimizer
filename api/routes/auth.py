from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from application.services.application_service import ApplicationService
from application.dtos.auth_dto import LoginResponse, OAuthAuthorizationResponse
from application.dtos.user_dto import UserResponse
from application.commands.auth_command import LoginCommand
from application.commands.oauth_command import OAuthLoginCommand, OAuthAuthorizationCommand
from domain.organization.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)
from domain.organization.entities.user import User
from infrastructure.dependencies.service_container import get_application_service
from api.dependencies.auth import get_current_user_from_cookie

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    form_data: OAuth2PasswordRequestForm = Depends()
) -> LoginResponse:
    """Authenticate user and return user data with httpOnly cookies."""
    
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
        
        # Set tokens in httpOnly cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600  # 1 hour
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800  # 7 days
        )
        
        return LoginResponse(
            access_token="",  # Don't return tokens in response body
            refresh_token="",
            token_type="bearer",
            user_id=user.id.value,
            tenant_id=user.tenant_id,
            role=user.role.value,
            email=str(user.email),
            full_name=user.full_name
        )
    
    except (InvalidCredentialsError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    except InactiveUserError:
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


@router.post("/logout")
async def logout(response: Response):
    """Logout and clear httpOnly cookies."""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)]
) -> UserResponse:
    """Get current authenticated user information."""
    return UserResponse(
        user_id=str(current_user.id.value) if current_user.id else "",
        email=str(current_user.email),
        role=current_user.role.value,
        full_name=current_user.full_name,
        tenant_id=str(current_user.tenant_id) if current_user.tenant_id else "",
        is_active=current_user.is_active()
    )


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> Dict[str, Any]:
    """Refresh access token using refresh token."""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    try:
        # Validate refresh token and get new tokens (with rotation)
        user, new_access_token, new_refresh_token = await app_service.auth_use_cases.refresh_token(refresh_token)
        
        # Set new access token cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600  # 1 hour
        )
        
        # Set new refresh token cookie (rotation)
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800  # 7 days
        )
        
        return {
            "message": "Tokens refreshed successfully",
            "user": {
                "user_id": user.id.value if user.id else "",
                "email": str(user.email),
                "role": user.role.value,
                "full_name": user.full_name,
                "tenant_id": user.tenant_id
            }
        }
        
    except AuthenticationError as e:
        # Clear cookies if refresh fails
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        # Clear cookies if refresh fails
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
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
    response: Response,  # Add Response parameter
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
        
        # Create a response that will redirect to frontend
        success_url = f"{app_service.config.frontend_url}/auth/success?new_user={is_new_user}&provider={provider}"
        redirect_response = RedirectResponse(url=success_url)
        
        # Set httpOnly cookies instead of URL parameters
        redirect_response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600  # 1 hour
        )
        
        redirect_response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800  # 7 days
        )
        
        return redirect_response
        
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

