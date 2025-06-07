from typing import Annotated, Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel

from application.services.application_service import ApplicationService
from domain.organization.entities.user import User
from infrastructure.dependencies.service_container import get_application_service
from api.dependencies.auth import get_current_user_from_cookie

router = APIRouter(prefix="/auth", tags=["token-revocation"])


def _group_sessions_by_device(sessions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group sessions by device info."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for session in sessions:
        device_key = session.get("device_info", "Unknown Device")
        if device_key not in grouped:
            grouped[device_key] = []
        grouped[device_key].append(session)
    return grouped


def _group_sessions_by_ip(sessions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group sessions by IP address."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for session in sessions:
        ip_key = session.get("ip_address", "Unknown IP")
        if ip_key not in grouped:
            grouped[ip_key] = []
        grouped[ip_key].append(session)
    return grouped


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
    current_user: User = Depends(get_current_user_from_cookie),
    page: int = 1,
    page_size: int = 10,
    group_by: Optional[str] = None
) -> Dict[str, Any]:
    """Get list of active sessions for user with pagination and optional grouping."""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # Validate group_by parameter
        valid_group_options: List[Optional[str]] = ['device', 'ip', None]
        if group_by not in valid_group_options:
            group_by = None
        
        # Use grouped method if grouping is requested
        if group_by:
            result = await app_service.token_revocation_use_cases.get_user_active_sessions_grouped(
                current_user, group_by, page, page_size
            )
            
            # For grouped results, format the response differently
            grouped_sessions = result.get("grouped_sessions", {})
            formatted_grouped = {}
            
            for key, sessions in grouped_sessions.items():
                formatted_sessions: List[Dict[str, Any]] = []
                for session in sessions:
                    formatted_sessions.append({
                        "id": session["id"],
                        "device_info": session.get("device_info", "Unknown Device"),
                        "ip_address": session.get("ip_address", "Unknown IP"),
                        "user_agent": session.get("user_agent", "Unknown Browser"),
                        "created_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                        "expires_at": session["expires_at"].isoformat() if session.get("expires_at") and hasattr(session["expires_at"], 'isoformat') else None,                        "last_used_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                        "is_current": False
                    })
                formatted_grouped[key] = formatted_sessions
            
            return {
                "grouped_sessions": formatted_grouped,
                "grouping": group_by,
                "total_sessions": result.get("total_sessions", 0),
                "total_groups": result.get("total_devices", result.get("total_ips", len(grouped_sessions))),
                "page": result.get("page", page),
                "page_size": result.get("page_size", page_size),
                "total_pages": result.get("total_pages", 0)
            }
        else:
            # Regular ungrouped method
            result = await app_service.token_revocation_use_cases.get_user_active_sessions(
                current_user, page, page_size
            )
            
            # Format sessions for frontend consumption
            formatted_sessions: List[Dict[str, Any]] = []
            for session in result.get("sessions", []):
                formatted_sessions.append({
                    "id": session["id"],
                    "device_info": session.get("device_info", "Unknown Device"),
                    "ip_address": session.get("ip_address", "Unknown IP"),
                    "user_agent": session.get("user_agent", "Unknown Browser"),
                    "created_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                    "expires_at": session["expires_at"].isoformat() if session.get("expires_at") and hasattr(session["expires_at"], 'isoformat') else None,
                    "last_used_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                    "is_current": False
                })
            
            return {
                "sessions": formatted_sessions,
                "grouping": None,
                "total_count": result.get("total_count", 0),
                "page": result.get("page", page),
                "page_size": result.get("page_size", page_size),
                "total_pages": result.get("total_pages", 0)
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.get("/sessions/revoked")
async def get_revoked_sessions(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie),
    page: int = 1,
    page_size: int = 10,
    group_by: Optional[str] = None
) -> Dict[str, Any]:
    """Get list of revoked sessions for user with pagination and optional grouping."""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # Validate group_by parameter
        valid_group_options: List[Optional[str]] = ['device', 'ip', None]
        if group_by not in valid_group_options:
            group_by = None
        
        # Use grouped method if grouping is requested
        if group_by:
            result = await app_service.token_revocation_use_cases.get_user_revoked_sessions_grouped(
                current_user, group_by, page, page_size
            )
            
            # For grouped results, format the response differently
            grouped_sessions = result.get("grouped_sessions", {})
            formatted_grouped = {}
            
            for key, sessions in grouped_sessions.items():
                formatted_sessions: List[Dict[str, Any]] = []
                for session in sessions:
                    formatted_sessions.append({
                        "id": session["id"],
                        "device_info": session.get("device_info", "Unknown Device"),
                        "ip_address": session.get("ip_address", "Unknown IP"),
                        "user_agent": session.get("user_agent", "Unknown Browser"),
                        "created_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                        "expires_at": session["expires_at"].isoformat() if session.get("expires_at") and hasattr(session["expires_at"], 'isoformat') else None,
                        "revoked_at": session["revoked_at"].isoformat() if session.get("revoked_at") and hasattr(session["revoked_at"], 'isoformat') else None,
                        "is_current": False
                    })
                formatted_grouped[key] = formatted_sessions
            
            return {
                "grouped_sessions": formatted_grouped,
                "grouping": group_by,
                "total_sessions": result.get("total_sessions", 0),
                "total_groups": result.get("total_devices", result.get("total_ips", len(grouped_sessions))),
                "page": result.get("page", page),
                "page_size": result.get("page_size", page_size),
                "total_pages": result.get("total_pages", 0)
            }
        else:
            # Regular ungrouped method
            result = await app_service.token_revocation_use_cases.get_user_revoked_sessions(
                current_user, page, page_size
            )
            
            # Format sessions for frontend consumption
            formatted_sessions: List[Dict[str, Any]] = []
            for session in result.get("sessions", []):
                formatted_sessions.append({
                    "id": session["id"],
                    "device_info": session.get("device_info", "Unknown Device"),
                    "ip_address": session.get("ip_address", "Unknown IP"),
                    "user_agent": session.get("user_agent", "Unknown Browser"),
                    "created_at": session["created_at"].isoformat() if session.get("created_at") and hasattr(session["created_at"], 'isoformat') else None,
                    "expires_at": session["expires_at"].isoformat() if session.get("expires_at") and hasattr(session["expires_at"], 'isoformat') else None,
                    "revoked_at": session["revoked_at"].isoformat() if session.get("revoked_at") and hasattr(session["revoked_at"], 'isoformat') else None,
                    "is_current": False
                })
            
            return {
                "sessions": formatted_sessions,
                "grouping": None,
                "total_count": result.get("total_count", 0),
                "page": result.get("page", page),
                "page_size": result.get("page_size", page_size),
                "total_pages": result.get("total_pages", 0)
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get revoked sessions: {str(e)}"
        )


@router.get("/refresh-tokens")
async def get_user_refresh_tokens(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie),
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """Get user's refresh tokens from database for session management display with pagination."""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
            
        result = await app_service.token_revocation_use_cases.get_user_active_sessions(
            current_user, page, page_size
        )
        
        # Format the response for frontend consumption
        formatted_sessions: List[Dict[str, Any]] = []
        for session in result.get("sessions", []):
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
            "total_count": result.get("total_count", 0),
            "page": result.get("page", page),
            "page_size": result.get("page_size", page_size),
            "total_pages": result.get("total_pages", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get refresh tokens: {str(e)}"
        )


class RevokeSessionRequest(BaseModel):
    """Request to revoke a specific session by ID."""
    session_id: str


@router.post("/revoke-session")
async def revoke_session_by_id(
    request: RevokeSessionRequest,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)
) -> Dict[str, Any]:
    """Revoke a specific session by its database ID."""
    try:
        success = await app_service.token_revocation_use_cases.revoke_session_by_id(
            request.session_id,
            current_user
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or already revoked"
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
