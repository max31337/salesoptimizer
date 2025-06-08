#!/usr/bin/env python3
"""
Superadmin Management Service - Enforces single superadmin constraint.
This service ensures only one superadmin exists in the system at any time.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from domain.organization.entities.user import UserRole
from infrastructure.db.models.user_model import UserModel


class SuperadminManagementService:
    """Service for managing superadmin constraints and operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_existing_superadmin(self) -> Optional[UserModel]:
        """Get the existing superadmin if one exists."""
        return self.session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).first()
    
    def count_superadmins(self) -> int:
        """Count the number of existing superadmins."""
        return self.session.query(func.count(UserModel.id)).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).scalar() or 0
    
    def get_all_superadmins(self) -> List[UserModel]:
        """Get all existing superadmins."""
        return self.session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).all()
    
    def can_create_superadmin(self) -> bool:
        """Check if a new superadmin can be created (system constraint: max 1)."""
        return self.count_superadmins() == 0
    
    def validate_single_superadmin_constraint(self) -> Dict[str, Any]:
        """Validate that only one superadmin exists and return validation result."""
        superadmins = self.get_all_superadmins()
        count = len(superadmins)
        
        return {
            "is_valid": count <= 1,
            "current_count": count,
            "max_allowed": 1,
            "superadmins": [
                {
                    "id": str(admin.id),
                    "email": admin.email,
                    "username": admin.username,
                    "created_at": admin.created_at.isoformat() if admin.created_at else None
                }
                for admin in superadmins
            ],
            "violation_message": f"System constraint violation: {count} superadmins found, maximum allowed is 1" if count > 1 else None
        }
    
    def ensure_single_superadmin_constraint(self, keep_latest: bool = True) -> Dict[str, Any]:
        """
        Ensure only one superadmin exists by removing extras.
        
        Args:
            keep_latest: If True, keep the most recently created superadmin.
                        If False, keep the first created superadmin.
        
        Returns:
            dict with operation result and details
        """
        validation = self.validate_single_superadmin_constraint()
        
        if validation["is_valid"]:
            return {
                "action": "none_required",
                "message": "Single superadmin constraint already satisfied",
                "details": validation
            }
        
        superadmins = validation["superadmins"]
        
        if len(superadmins) == 0:
            return {
                "action": "no_superadmins",
                "message": "No superadmins found in the system",
                "details": validation
            }
        
        # Sort superadmins by creation date
        sorted_superadmins = sorted(
            self.get_all_superadmins(),
            key=lambda x: x.created_at or datetime.min,
            reverse=keep_latest  # True = latest first, False = earliest first
        )
        
        # Keep the first one (latest or earliest based on sort)
        superadmin_to_keep = sorted_superadmins[0]
        superadmins_to_remove = sorted_superadmins[1:]
        
        removed_details: List[Dict[str, Any]] = []
        for admin in superadmins_to_remove:
            removed_details.append({
                "id": str(admin.id),
                "email": admin.email,
                "username": admin.username,
                "created_at": admin.created_at.isoformat() if admin.created_at else None
            })
            # Instead of deleting, change role to org_admin
            admin.role = UserRole.ORG_ADMIN
            admin.updated_at = datetime.now(timezone.utc)
        
        self.session.flush()  # Apply changes without committing
        
        return {
            "action": "constraint_enforced",
            "message": f"Enforced single superadmin constraint: kept 1, demoted {len(superadmins_to_remove)} to org_admin",
            "kept_superadmin": {
                "id": str(superadmin_to_keep.id),
                "email": superadmin_to_keep.email,
                "username": superadmin_to_keep.username,
                "created_at": superadmin_to_keep.created_at.isoformat() if superadmin_to_keep.created_at else None
            },
            "demoted_superadmins": removed_details,
            "strategy": "keep_latest" if keep_latest else "keep_earliest"
        }


# Helper function for backward compatibility
def validate_superadmin_limit(session: Session) -> Dict[str, Any]:
    """Validate superadmin limit constraint."""
    service = SuperadminManagementService(session)
    return service.validate_single_superadmin_constraint()


def enforce_single_superadmin(session: Session, keep_latest: bool = True) -> Dict[str, Any]:
    """Enforce single superadmin constraint."""
    service = SuperadminManagementService(session)
    return service.ensure_single_superadmin_constraint(keep_latest)
