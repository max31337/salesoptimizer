from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infrastructure.dependencies.service_container import get_application_service
from application.services.application_service import ApplicationService
from domain.organization.entities.user import User
from domain.organization.value_objects.user_role import Permission

security = HTTPBearer()


async def get_current_user(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Extract current user from JWT token in Authorization header."""
    # Verify token using auth service
    payload = await app_service.auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Get user ID from token payload
    user_id_str = payload.get("sub")  # JWT 'sub' claim contains user ID
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user from database
    user = await app_service.auth_service.get_user_by_id(user_id_str)
    if not user or not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


async def get_current_user_from_cookie(
    request: Request,
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
) -> User:
    """Extract user from httpOnly cookie token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get token from httpOnly cookie
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
    
    try:
        # Verify and decode token through auth service (includes revocation check)
        payload = await app_service.auth_service.verify_token(token)  # Now async!
        if not payload:
            raise credentials_exception
        
        # Extract user ID from payload
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
            
        # Get user from database
        user = await app_service.auth_service.get_user_by_id(user_id_str)
        if user is None or not user.is_active():
            raise credentials_exception 
        
        return user
    except Exception:
        raise credentials_exception


async def get_optional_current_user(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Extract current user from JWT token, return None if not authenticated."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(app_service, credentials)
    except HTTPException:
        return None


def require_permission(permission: Permission):
    """Create a dependency that requires a specific permission."""
    def permission_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return current_user
    return permission_dependency


def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require super admin role (using domain logic)."""
    if not current_user.has_permission(Permission.MANAGE_SYSTEM):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def require_tenant_creation(current_user: User = Depends(get_current_user)) -> User:
    """Require tenant creation permission."""
    return require_permission(Permission.CREATE_TENANT)(current_user)


def require_invitation_creation(current_user: User = Depends(get_current_user)) -> User:
    """Require invitation creation permission."""
    return require_permission(Permission.CREATE_INVITATION)(current_user)


def require_invitation_and_tenant_creation(current_user: User = Depends(get_current_user)) -> User:
    """Require both invitation creation and tenant creation permissions."""
    if not current_user.has_permission(Permission.CREATE_INVITATION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission required: create invitations"
        )
    
    if not current_user.has_permission(Permission.CREATE_TENANT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission required: create tenants"
        )
    return current_user


def require_system_management(current_user: User = Depends(get_current_user)) -> User:
    """Require system management permission."""
    return require_permission(Permission.MANAGE_SYSTEM)(current_user)


def require_org_management(current_user: User = Depends(get_current_user)) -> User:
    """Require organization management permission."""
    return require_permission(Permission.MANAGE_ORGANIZATION)(current_user)