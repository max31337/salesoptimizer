from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID

from infrastructure.db.base import get_db
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.services.jwt_service import JWTService
from domain.entities.user import User, UserStatus, UserRole

security: HTTPBearer = HTTPBearer()

def get_jwt_service() -> JWTService:
    """Get JWT service instance."""
    return JWTService()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    token: str = credentials.credentials
    
    # Verify token
    payload: Optional[Dict[str, Any]] = jwt_service.verify_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID
    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id: UUID = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_repo: UserRepositoryImpl = UserRepositoryImpl(db)
    user: Optional[User] = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check)."""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be a super admin."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user

def require_org_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be an organization admin or higher."""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access required"
        )
    return current_user

def require_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be a manager or higher."""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user

def require_admin_or_self(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be admin or accessing their own data."""
    try:
        target_user_id: UUID = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Allow if user is admin
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        return current_user
    
    # Allow if user is accessing their own data
    if current_user.id == target_user_id:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )

def require_same_tenant(
    tenant_id: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to belong to the same tenant or be super admin."""
    try:
        target_tenant_id: UUID = UUID(tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format"
        )
    
    # Super admins can access any tenant
    if current_user.role == UserRole.SUPER_ADMIN:
        return current_user
    
    # Check if user belongs to the same tenant
    if current_user.tenant_id != target_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - different tenant"
        )
    
    return current_user

def require_tenant_admin(
    tenant_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be admin of the specified tenant."""
    # Super admins can access any tenant
    if current_user.role == UserRole.SUPER_ADMIN:
        return current_user
    
    # Organization admins can only access their own tenant
    if current_user.role == UserRole.ORG_ADMIN:
        if tenant_id:
            try:
                target_tenant_id: UUID = UUID(tenant_id)
                if current_user.tenant_id != target_tenant_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied - different tenant"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tenant ID format"
                )
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Tenant admin access required"
    )

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None."""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, jwt_service, db)
    except HTTPException:
        return None

def require_email_verified(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to have verified email."""
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user

def get_current_user_permissions(
    current_user: User = Depends(get_current_user)
) -> Dict[str, bool]:
    """Get current user's permissions based on role."""
    permissions: Dict[str, bool] = {
        "can_manage_users": current_user.can_manage_users(),
        "is_admin": current_user.is_admin(),
        "is_super_admin": current_user.role == UserRole.SUPER_ADMIN,
        "is_org_admin": current_user.role == UserRole.ORG_ADMIN,
        "is_manager": current_user.role == UserRole.MANAGER,
        "is_sales_rep": current_user.role == UserRole.SALES_REP,
        "can_access_all_tenants": current_user.role == UserRole.SUPER_ADMIN,
        "can_manage_tenant": current_user.role in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN],
        "is_email_verified": current_user.is_email_verified,
        "is_active": current_user.status == UserStatus.ACTIVE
    }
    return permissions