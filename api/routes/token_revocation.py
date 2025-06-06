from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel

from application.services.application_service import ApplicationService
from domain.organization.entities.user import User
from infrastructure.dependencies.service_container import get_application_service
from api.dependencies.auth import get_current_user_from_cookie

router = APIRouter(prefix="/auth", tags=["token-revocation"])


class LogoutAllDevicesRequest(BaseModel):
    """Request to logout from all devices."""
    confirm: bool = True


@router.post("/logout-current")
async def logout_current_device(
    request: Request,
    response: Response,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Logout from current device only."""
    # Get tokens from cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    if not access_token or not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tokens found"
        )
    
    try:
        # Revoke current device tokens
        success = await app_service.token_revocation_use_cases.logout_current_device(
            current_user,
            access_token,
            refresh_token
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke tokens"
            )
        
        # Clear cookies
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        
        return {
            "message": "Successfully logged out from current device",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/logout-all-devices")
async def logout_all_devices(
    request: LogoutAllDevicesRequest,
    response: Response,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Logout from all devices."""
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required"
        )
    
    try:
        # Revoke all user tokens
        success = await app_service.token_revocation_use_cases.logout_all_devices(current_user)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke all tokens"
            )
        
        # Clear current device cookies
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        
        return {
            "message": "Successfully logged out from all devices",
            "success": True,
            "devices_affected": "all"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout from all devices failed: {str(e)}"
        )


@router.get("/sessions")
async def get_active_sessions(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Get list of active sessions for user."""
    try:
        sessions = await app_service.token_revocation_use_cases.get_user_active_sessions(current_user)
        
        return {
            "sessions": sessions,
            "total_count": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.post("/revoke-token")
async def revoke_specific_token(
    token: str,
    response: Response,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Revoke a specific token."""
    try:
        success = await app_service.token_revocation_use_cases.revoke_specific_token(
            token,
            current_user
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke token"
            )
        
        # Clear cookies
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        
        return {
            "message": "Token revoked successfully",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token revocation failed: {str(e)}"
        )