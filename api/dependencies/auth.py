from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.database import get_async_session
from infrastructure.services.jwt_service import JWTService
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from domain.organization.entities.user import User
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.user_role import Permission  # Import Permission enum

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """Extract current user from JWT token."""
    jwt_service = JWTService()
    user_repository = UserRepositoryImpl(session)
    
    # Verify token
    token_data = jwt_service.verify_token(credentials.credentials)
    if not token_data or token_data.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Get user
    user_id_str = token_data.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        user_id = UserId.from_string(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    user = await user_repository.get_by_id(user_id)
    if not user or not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> Optional[User]:
    """Extract current user from JWT token, return None if not authenticated."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None


# ✅ FIXED: Use domain permission system
def require_permission(permission: Permission):
    """Create a dependency that requires a specific permission."""
    def permission_dependency(current_user: User = Depends(get_current_user)) -> User:
        print(f"🔍 Checking permission: {permission.value}")
        print(f"🔍 User role: {current_user.role.value}")
        print(f"🔍 Has permission: {current_user.has_permission(permission)}")
        
        if not current_user.has_permission(permission):
            print(f"❌ Access denied for permission: {permission.value}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return current_user
    return permission_dependency


# ✅ FIXED: Use domain permission instead of direct role check
def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require super admin role (using domain logic)."""
    print(f"🔍 Checking super admin access")
    print(f"🔍 User role: {current_user.role.value}")
    print(f"🔍 Has system management permission: {current_user.has_permission(Permission.MANAGE_SYSTEM)}")
    
    if not current_user.has_permission(Permission.MANAGE_SYSTEM):
        print(f"❌ Access denied - not super admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


# ✅ DOMAIN-DRIVEN: Use Permission enum
def require_tenant_creation(current_user: User = Depends(get_current_user)) -> User:
    """Require tenant creation permission."""
    return require_permission(Permission.CREATE_TENANT)(current_user)


def require_invitation_creation(current_user: User = Depends(get_current_user)) -> User:
    """Require invitation creation permission."""
    return require_permission(Permission.CREATE_INVITATION)(current_user)


def require_invitation_and_tenant_creation(current_user: User = Depends(get_current_user)) -> User:
    """Require both invitation creation and tenant creation permissions."""
    print(f"🔍 Checking invitation + tenant creation permissions")
    print(f"🔍 User role: {current_user.role.value}")
    print(f"🔍 Can create invitations: {current_user.has_permission(Permission.CREATE_INVITATION)}")
    print(f"🔍 Can create tenants: {current_user.has_permission(Permission.CREATE_TENANT)}")
    
    if not current_user.has_permission(Permission.CREATE_INVITATION):
        print(f"❌ Access denied for invitation creation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission required: create invitations"
        )
    
    if not current_user.has_permission(Permission.CREATE_TENANT):
        print(f"❌ Access denied for tenant creation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission required: create tenants"
        )
    return current_user


# ✅ DOMAIN-DRIVEN: System administration permission
def require_system_management(current_user: User = Depends(get_current_user)) -> User:
    """Require system management permission."""
    return require_permission(Permission.MANAGE_SYSTEM)(current_user)


# ✅ DOMAIN-DRIVEN: Organization management permission  
def require_org_management(current_user: User = Depends(get_current_user)) -> User:
    """Require organization management permission."""
    return require_permission(Permission.MANAGE_ORGANIZATION)(current_user)