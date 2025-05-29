from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from infrastructure.db.base import get_db
from infrastructure.services.jwt_service import JWTService
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from domain.entities.user import User, UserRole

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract current user from JWT token."""
    jwt_service = JWTService()
    
    try:
        payload = jwt_service.decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    from uuid import UUID

    user_repo = UserRepositoryImpl(db)
    try:
        user_uuid = UUID(str(user_id))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    user = user_repo.get_by_id(user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extract current user from JWT token, return None if not authenticated."""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def require_role(required_role: UserRole):
    """Dependency factory to require specific role."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role.value}"
            )
        return current_user
    return role_checker

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require super admin role."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user

def require_org_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require org admin or super admin role."""
    if current_user.role not in [UserRole.ORG_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access required"
        )
    return current_user

def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """Require manager, org admin, or super admin role."""
    if current_user.role not in [UserRole.MANAGER, UserRole.ORG_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user