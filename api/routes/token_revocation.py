from typing import Annotated, Dict, Any, List
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
        
        # Format sessions for frontend consumption
        formatted_sessions: List[Dict[str, Any]] = []
        for session in sessions:
            formatted_sessions.append({
                "id": session["id"],
                "device_info": session.get("device_info", "Unknown Device"),
                "ip_address": session.get("ip_address", "Unknown IP"),
                "user_agent": session.get("user_agent", "Unknown Browser"),
                "created_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                "expires_at": session["expires_at"].isoformat() if session.get("expires_at") and hasattr(session["expires_at"], 'isoformat') else None,
                "last_used_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,  # Use created_at as last_used_at for now
                "is_current": False  # TODO: Determine if this is the current session
            })
        
        return {
            "sessions": formatted_sessions,
            "total_count": len(formatted_sessions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.get("/refresh-tokens")
async def get_user_refresh_tokens(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Get user's refresh tokens from database for session management display."""
    try:
        sessions = await app_service.token_revocation_use_cases.get_user_active_sessions(current_user)
        
        # Format the response for frontend consumption
        formatted_sessions: List[Dict[str, Any]] = []
        for session in sessions:
            formatted_sessions.append({
                "id": session["id"],
                "device_info": session.get("device_info", "Unknown Device"),
                "ip_address": session.get("ip_address", "Unknown IP"),
                "user_agent": session.get("user_agent", "Unknown Browser"),
                "created_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                "expires_at": session["expires_at"].isoformat() if session.get("expires_at") and hasattr(session["expires_at"], 'isoformat') else None,
                "is_current": False  # TODO: Determine if this is the current session
            })
        
        return {
            "refresh_tokens": formatted_sessions,
            "total_count": len(formatted_sessions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get refresh tokens: {str(e)}"
        )


class RevokeSessionRequest(BaseModel):
    """Request to revoke a specific session."""
    session_id: str


@router.post("/revoke-session")
async def revoke_session(
    request: RevokeSessionRequest,
    response: Response,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Revoke a specific session by session ID."""
    try:
        success = await app_service.token_revocation_use_cases.revoke_session_by_id(
            request.session_id,
            current_user
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke session"
            )
        
        return {
            "message": "Session revoked successfully",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session revocation failed: {str(e)}"
        )


class RevokeTokenRequest(BaseModel):
    """Request to revoke a specific token."""
    token: str


@router.post("/revoke-token")
async def revoke_specific_token(
    request: RevokeTokenRequest,
    response: Response,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Revoke a specific token."""
    try:
        success = await app_service.token_revocation_use_cases.revoke_specific_token(
            request.token,
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