from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse

from application.services.application_service import ApplicationService
from application.dtos.organization_dto import (
    OrganizationRegistrationRequest,
    OrganizationRegistrationResponse,
    InvitationSignupRequest,
    InvitationSignupResponse
)
from application.commands.organization_registration_command import OrganizationRegistrationCommand
from infrastructure.dependencies.service_container import get_application_service
from infrastructure.config.settings import settings


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/register", response_model=OrganizationRegistrationResponse)
async def register_organization(
    request: Request,
    response: Response,
    registration_request: OrganizationRegistrationRequest,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> OrganizationRegistrationResponse:
    """
    Self-serve organization registration.
    
    Allows new organizations to register for trial, basic, or pro plans.
    Creates both the organization and the admin user account.
    """
    
    try:
        # Validate the registration request
        if not registration_request.accept_terms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Terms of service must be accepted"
            )
        
        if not registration_request.accept_privacy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Privacy policy must be accepted"
            )
        
        if not registration_request.username or not registration_request.username.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required"
            )
        
        # Create command
        command = OrganizationRegistrationCommand(
            organization_name=registration_request.organization_name,
            organization_slug=registration_request.organization_slug,
            industry=registration_request.industry,
            organization_size=registration_request.organization_size,
            website=registration_request.website,
            username=registration_request.username,  # <-- Pass username
            first_name=registration_request.first_name,
            last_name=registration_request.last_name,
            email=registration_request.email,
            password=registration_request.password,
            job_title=registration_request.job_title,
            subscription_tier=registration_request.subscription_tier,  # <-- map plan to subscription_tier
            accept_terms=registration_request.accept_terms,
            accept_privacy=registration_request.accept_privacy,
            marketing_opt_in=registration_request.marketing_opt_in
        )
        
        # Register the organization
        # Note: This will need to be implemented in your application service
        # For now, let's create a basic version
        
        # Check if organization registration use case exists
        if not hasattr(app_service, 'organization_registration_use_cases'):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Organization registration is not yet implemented"
            )
        
        admin_user, tenant = await app_service.organization_registration_use_cases.register_organization(command)
        
        # Create tokens for the new user
        access_token, refresh_token = await app_service.auth_service.create_tokens(admin_user)
        
        # Validate that user ID exists
        if admin_user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing after registration"
            )
        
        # Set authentication cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",  # Use literal value instead of settings
            max_age=settings.JWT_EXPIRE_MINUTES * 60,
            domain=settings.cookie_domain,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",  # Use literal value instead of settings
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * settings.SECONDS_PER_DAY,
            domain=settings.cookie_domain,
            path="/"
        )
        
        return OrganizationRegistrationResponse(
            user_id=str(admin_user.id.value),
            email=str(admin_user.email),
            first_name=admin_user.first_name,
            last_name=admin_user.last_name,
            role=admin_user.role.value,
            tenant_id=str(tenant.id.value) if tenant.id is not None else "",
            organization_name=tenant.name,
            organization_slug=tenant.slug if tenant.slug is not None else "",
            subscription_tier=tenant.subscription_tier if tenant.subscription_tier is not None else "",
            message="Organization registered successfully! You are now logged in."
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register organization: {str(e)}"
        )


@router.post("/complete-invitation", response_model=InvitationSignupResponse)
async def complete_invitation_signup(
    request: Request,
    response: Response,
    signup_request: InvitationSignupRequest,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> InvitationSignupResponse:
    """
    Complete organization admin signup from invitation.
    
    This endpoint is used when a super admin has invited an organization admin,
    and the invited user is completing their account setup.
    """
    
    try:
        # Check if organization registration use case exists
        if not hasattr(app_service, 'organization_registration_use_cases'):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Invitation signup is not yet implemented"
            )
        
        admin_user, tenant, access_token, refresh_token = await app_service.organization_registration_use_cases.complete_invitation_signup(
            invitation_token=signup_request.invitation_token,
            first_name=signup_request.first_name,
            last_name=signup_request.last_name,
            password=signup_request.password,
            job_title=signup_request.job_title
        )
        
        # Validate that user ID exists
        if admin_user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing after signup"
            )
        
        # Set authentication cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            max_age=settings.JWT_EXPIRE_MINUTES * 60,
            domain=settings.cookie_domain,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * settings.SECONDS_PER_DAY,
            domain=settings.cookie_domain,
            path="/"
        )
        
        return InvitationSignupResponse(
            user_id=str(admin_user.id.value),
            email=str(admin_user.email),
            first_name=admin_user.first_name,
            last_name=admin_user.last_name,
            role=admin_user.role.value,
            tenant_id=str(admin_user.tenant_id),
            organization_name=tenant.name,
            message="Account setup completed successfully! You are now logged in."
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete invitation signup: {str(e)}"
        )


@router.get("/invitation/{token}")
async def get_invitation_details(
    token: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> dict[str, Any]:
    """
    Get invitation details for the signup form.
    
    This allows the frontend to pre-populate organization name and email
    when the user clicks on an invitation link.
    """
    
    try:
        invitation = await app_service.invitation_use_cases.get_invitation_by_token(token)
        
        return {
            "email": str(invitation.email),
            "organization_name": invitation.organization_name,
            "invited_by": "SalesOptimizer Admin",  # Default value since invited_by_name isn't available
            "expires_at": invitation.expires_at.isoformat() if invitation.expires_at else None,
            "is_valid": invitation.is_valid()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invitation details: {str(e)}"
        )


@router.get("/verify-email")
async def verify_email(
    token: str,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
):
    """
    Verify a user's email using the token and redirect to login with username pre-filled.
    """
    import logging
    import logging
    logger = logging.getLogger("verify-email")
    try:
        logger.info(f"[VERIFY-EMAIL] Received token: {token}")
        # Call the use case to verify the email
        status, username = await app_service.organization_registration_use_cases.verify_email(token)
        logger.info(f"[VERIFY-EMAIL] Verification result status: {status}, username: {username}")
        # Always include username param, even if None or empty
        username_param = f"&username={username}" if username else "&username="
        redirect_url = f"{settings.FRONTEND_URL}/verify-email?status={status}{username_param}"
        logger.info(f"[VERIFY-EMAIL] Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"[VERIFY-EMAIL] Exception during verification: {e}", exc_info=True)
        # Also include username param as empty for fail case
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/verify-email?status=fail&username=")
